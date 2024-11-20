import sys
import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

# Configure logging to output INFO level messages and above
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ResourceInfo:
    """Data class to store resource information."""
    arn: str
    type: str
    tags: Dict[str, str]
    details: Optional[Dict] = None  # Additional details fetched later


class AWSResourceInventory:
    def __init__(self, region: str):
        """Initialize the AWSResourceInventory with a specific AWS region."""
        self.region = region
        self.session = boto3.Session(region_name=region)
        # Client for Resource Groups Tagging API to list resources
        self.resource_groups_client = self.session.client('resourcegroupstaggingapi')
        self.resource_cache = {}  # Optional cache for resource details

        # Mapping between service names in ARN and boto3 client names
        self.service_mapping = {
            'ec2': 'ec2',
            'elasticloadbalancing': 'elbv2',  # Elastic Load Balancing v2
            's3': 's3',
            'rds': 'rds',
            'iam': 'iam',
            'route53': 'route53'
            # We can add other service mappings as needed, those are the resources I used in the assignment...
        }

    def get_all_resources(self) -> Dict[str, List[ResourceInfo]]:
        """Get all AWS resources in the region, including global services."""
        resources_by_service = defaultdict(list)

        try:
            # Use paginator to handle large number of resources
            paginator = self.resource_groups_client.get_paginator('get_resources')

            # Iterate over each page of resources
            for page in paginator.paginate():
                for resource in page['ResourceTagMappingList']:
                    # Extract service name from the resource ARN
                    service = self._extract_service_from_arn(resource['ResourceARN'])
                    # Create a ResourceInfo object and add it to the corresponding service list
                    resources_by_service[service].append(
                        ResourceInfo(
                            arn=resource['ResourceARN'],
                            type=self._extract_resource_type(resource['ResourceARN']),
                            tags=self._convert_tags_to_dict(resource.get('Tags', []))
                        )
                    )

            # Special handling for S3 and IAM since they are global services
            if 's3' not in resources_by_service:
                self._add_s3_resources(resources_by_service)

            # Add IAM resources to the inventory
            self._add_iam_resources(resources_by_service)

            # Add Route 53 resources to the inventory
            self._add_route53_resources(resources_by_service)

        except ClientError as e:
            logger.error(f"Error fetching resources: {e}")
            raise

        return dict(resources_by_service)

    def get_detailed_inventory(self, resources_by_service: Dict[str, List[ResourceInfo]]) -> Dict[str, List[ResourceInfo]]:
        """Get detailed information for each resource using parallel processing."""
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            # Submit a task for each service to fetch resource details
            for service, resources in resources_by_service.items():
                futures.append(
                    executor.submit(self._get_service_details, service, resources)
                )

            # Collect the results as they complete
            detailed_inventory = {}
            for future in as_completed(futures):
                service, resources = future.result()
                if resources:
                    detailed_inventory[service] = resources

        return detailed_inventory

    def _get_service_details(self, service: str, resources: List[ResourceInfo]) -> tuple:
        """Get detailed information for a specific service's resources."""
        try:
            # Get the appropriate boto3 client for the service
            boto3_service = self.service_mapping.get(service, service)
            client = self.session.client(boto3_service)

            # Call the corresponding method based on the service
            if service == 'ec2':
                resources = self._get_ec2_details(client, resources)
            elif service == 's3':
                resources = self._get_s3_details(client, resources)
            elif service == 'rds':
                resources = self._get_rds_details(client, resources)
            elif service == 'iam':
                resources = self._get_iam_details(client, resources)
            elif service == 'route53':
                resources = self._get_route53_details(client, resources)
            # We can add other service handlers as needed, those are the resources I used in the assignment...

            return service, resources

        except ClientError as e:
            logger.error(f"Error getting details for service {service}: {e}")
            return service, resources

    def _get_ec2_details(self, client, resources: List[ResourceInfo]) -> List[ResourceInfo]:
        """Get detailed information for EC2 resources."""
        # Extract instance IDs from the ARNs
        instance_ids = [
            r.arn.split('/')[-1] for r in resources
            if r.type == 'instance'
        ]

        if instance_ids:
            try:
                # Fetch details about the instances
                response = client.describe_instances(InstanceIds=instance_ids)
                instances_details = {}
                # Collect instance details
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        instances_details[instance['InstanceId']] = {
                            'State': instance['State']['Name'],
                            'Type': instance['InstanceType'],
                            'PrivateIP': instance.get('PrivateIpAddress'),
                            'PublicIP': instance.get('PublicIpAddress')
                        }

                # Update the details in the ResourceInfo objects
                for resource in resources:
                    if resource.type == 'instance':
                        instance_id = resource.arn.split('/')[-1]
                        resource.details = instances_details.get(instance_id)

            except ClientError as e:
                logger.error(f"Error getting EC2 instance details: {e}")

        return resources

    def _get_s3_details(self, client, resources: List[ResourceInfo]) -> List[ResourceInfo]:
        """Get detailed information for S3 buckets."""
        try:
            # List all S3 buckets
            response = client.list_buckets()
            buckets = {bucket['Name']: bucket for bucket in response['Buckets']}

            for resource in resources:
                bucket_name = resource.arn.split(':')[-1]
                if bucket_name in buckets:
                    # Get the bucket's location to confirm its region
                    location = client.get_bucket_location(Bucket=bucket_name)
                    bucket_region = location.get('LocationConstraint') or 'us-east-1'

                    # Only include buckets in the specified region
                    if bucket_region == self.region:
                        resource.details = {
                            'CreationDate': buckets[bucket_name]['CreationDate'].isoformat(),
                            'Region': bucket_region
                        }

        except ClientError as e:
            logger.error(f"Error getting S3 bucket details: {e}")

        return resources

    def _add_s3_resources(self, resources_by_service: Dict[str, List[ResourceInfo]]):
        """Add S3 buckets for the specified region."""
        try:
            s3_client = self.session.client('s3')
            response = s3_client.list_buckets()

            # Iterate over all buckets and add those that match the region
            for bucket in response['Buckets']:
                try:
                    # Get the bucket's region
                    location = s3_client.get_bucket_location(Bucket=bucket['Name'])
                    bucket_region = location.get('LocationConstraint') or 'us-east-1'

                    if bucket_region == self.region:
                        arn = f"arn:aws:s3:::{bucket['Name']}"
                        # Add the bucket to the resources list for S3
                        resources_by_service['s3'].append(
                            ResourceInfo(
                                arn=arn,
                                type='bucket',
                                tags={},  # Optionally fetch tags with get_bucket_tagging
                                details={
                                    'CreationDate': bucket['CreationDate'].isoformat(),
                                    'Region': bucket_region
                                }
                            )
                        )
                except ClientError as e:
                    # Ignore buckets that cannot be accessed due to permissions
                    if e.response['Error']['Code'] != 'NoSuchBucket':
                        logger.error(f"Error getting bucket location for {bucket['Name']}: {e}")

        except ClientError as e:
            logger.error(f"Error listing S3 buckets: {e}")

    def _add_iam_resources(self, resources_by_service: Dict[str, List[ResourceInfo]]):
        """Add IAM resources (users and roles)."""
        try:
            iam_client = self.session.client('iam')

            # Add IAM Users
            users_response = iam_client.list_users()
            for user in users_response['Users']:
                resources_by_service['iam'].append(
                    ResourceInfo(
                        arn=user['Arn'],
                        type='user',
                        tags={},  # Optionally fetch tags with list_user_tags
                        details={
                            'UserId': user['UserId'],
                            'UserName': user['UserName'],
                            'CreationDate': user['CreateDate'].isoformat()
                        }
                    )
                )

            # Add IAM Roles
            roles_response = iam_client.list_roles()
            for role in roles_response['Roles']:
                resources_by_service['iam'].append(
                    ResourceInfo(
                        arn=role['Arn'],
                        type='role',
                        tags={},  # Optionally fetch tags with list_role_tags
                        details={
                            'RoleId': role['RoleId'],
                            'RoleName': role['RoleName'],
                            'CreationDate': role['CreateDate'].isoformat()
                        }
                    )
                )

        except ClientError as e:
            logger.error(f"Error listing IAM resources: {e}")

    def _add_route53_resources(self, resources_by_service: Dict[str, List[ResourceInfo]]):
        """Add Route 53 resources (hosted zones)."""
        try:
            route53_client = self.session.client('route53')

            # List all hosted zones
            hosted_zones_response = route53_client.list_hosted_zones()
            for zone in hosted_zones_response['HostedZones']:
                resources_by_service['route53'].append(
                    ResourceInfo(
                        arn=zone['Id'],  # The ID is sufficient for Route 53
                        type='hosted_zone',
                        tags={},  # Optionally fetch tags with list_tags_for_resource
                        details={
                            'Name': zone['Name'],
                            'CallerReference': zone['CallerReference'],
                            'Config': zone.get('Config', {}),
                            'ResourceRecordSetCount': zone['ResourceRecordSetCount']
                        }
                    )
                )

        except ClientError as e:
            logger.error(f"Error listing Route 53 resources: {e}")

    def _get_rds_details(self, client, resources: List[ResourceInfo]) -> List[ResourceInfo]:
        """Placeholder for RDS details if needed."""
        # Implement RDS details retrieval if required
        return resources

    def _get_iam_details(self, client, resources: List[ResourceInfo]) -> List[ResourceInfo]:
        """Get detailed information for IAM resources."""
        try:
            for resource in resources:
                if resource.type == 'user':
                    # Fetch tags for the IAM user
                    tags_response = client.list_user_tags(UserName=resource.details['UserName'])
                    resource.tags = {tag['Key']: tag['Value'] for tag in tags_response['Tags']}
                elif resource.type == 'role':
                    # Fetch tags for the IAM role
                    tags_response = client.list_role_tags(RoleName=resource.details['RoleName'])
                    resource.tags = {tag['Key']: tag['Value'] for tag in tags_response['Tags']}

        except ClientError as e:
            logger.error(f"Error getting IAM resource details: {e}")

        return resources

    def _get_route53_details(self, client, resources: List[ResourceInfo]) -> List[ResourceInfo]:
        """Get detailed information for Route 53 resources."""
        try:
            for resource in resources:
                if resource.type == 'hosted_zone':
                    # Fetch record sets for the hosted zone
                    record_sets = client.list_resource_record_sets(HostedZoneId=resource.arn)
                    resource.details['RecordSets'] = [
                        {
                            'Name': record_set['Name'],
                            'Type': record_set['Type'],
                            'TTL': record_set.get('TTL'),
                        } for record_set in record_sets['ResourceRecordSets']
                    ]

        except ClientError as e:
            logger.error(f"Error getting Route 53 resource details: {e}")

        return resources

    @staticmethod
    def _extract_service_from_arn(arn: str) -> str:
        """Extract the service name from an ARN."""
        return arn.split(':')[2]

    @staticmethod
    def _extract_resource_type(arn: str) -> str:
        """Extract the resource type from an ARN."""
        resource_part = arn.split(':')[-1]
        # For resources with '/', extract the type before the '/'
        return resource_part.split('/')[0] if '/' in resource_part else 'bucket'

    @staticmethod
    def _convert_tags_to_dict(tags: List[Dict[str, str]]) -> Dict[str, str]:
        """Convert a list of tag dictionaries to a single dictionary."""
        return {tag['Key']: tag['Value'] for tag in tags}


def main():
    if len(sys.argv) != 2:
        logger.error("Usage: python aws_resource_inventory.py <region>")
        sys.exit(1)

    region = sys.argv[1]

    try:
        # Create an instance of AWSResourceInventory
        inventory = AWSResourceInventory(region)

        # Get all resources in the specified region
        logger.info(f"Fetching resources in region {region}...")
        resources_by_service = inventory.get_all_resources()

        # Print a summary of services used
        print("\nServices used in region:", region)
        for service in resources_by_service.keys():
            print(f"  - {service} ({len(resources_by_service[service])} resources)")

        # Fetch and print detailed information about the resources
        logger.info("Fetching detailed resource information...")
        detailed_inventory = inventory.get_detailed_inventory(resources_by_service)

        print("\nDetailed Resource Inventory:")
        for service, resources in detailed_inventory.items():
            print(f"\n{service.upper()} Resources:")
            for resource in resources:
                print(f"  - ARN: {resource.arn}")
                print(f"    Type: {resource.type}")
                if resource.details:
                    print(f"    Details: {resource.details}")
                if resource.tags:
                    print(f"    Tags: {resource.tags}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
