import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import boto3

from NmapSlackMonitor.target_provider import TargetProvider


def _flatten(iterable):
    return (item for sublist in iterable for item in sublist)


@dataclass(frozen=True)
class AwsAPI(TargetProvider):
    session: boto3.Session

    def get_ips(self) -> List[Tuple[str, Optional[str]]]:
        # We have to pick one to start with
        ec2 = self.session.client('ec2', region_name='us-east-1')
        response = ec2.describe_regions()
        # Figure out where all the other regions are
        regions = [region['RegionName'] for region in response['Regions']]

        all_ips = []
        for region in regions:
            region_client = self.session.client('ec2', region_name=region)
            reservations = region_client.describe_instances()['Reservations']
            instances = _flatten(
                (reservation['Instances'] for reservation in reservations)
            )
            ips = [instance['PublicIpAddress'] for instance in instances if 'PublicIpAddress' in instance]
            all_ips.extend((ips, None))
        return []

    @staticmethod
    def authenticate(
            profile=None,
            aws_access_key_id=None,
            aws_secret_access_key=None,
            aws_session_token=None
    ):

        try:
            # Set logging level to error for libraries as otherwise generates a lot of warnings
            logging.getLogger('botocore').setLevel(logging.ERROR)
            logging.getLogger('botocore.auth').setLevel(logging.ERROR)
            logging.getLogger('urllib3').setLevel(logging.ERROR)

            if profile:
                session = boto3.Session(profile_name=profile)
            elif aws_access_key_id and aws_secret_access_key:
                if aws_session_token:
                    session = boto3.Session(
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        aws_session_token=aws_session_token,
                    )
                else:
                    session = boto3.Session(
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                    )
            else:
                session = boto3.Session()

            # Test querying for current user
            # AwsAPI._get_caller_identity(session)

            return AwsAPI(session=session)

        except Exception as e:
            raise Exception("Authentication Exception", e)

    @staticmethod
    def _get_caller_identity(session: boto3.Session):
        sts_client = session.resource('sts')
        identity = sts_client.get_caller_identity()
        return identity
