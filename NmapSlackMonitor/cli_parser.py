import argparse


class ScannerArgumentParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Run a regular NMAP Scan of your Network and post changes to Slack'
        )
        self.common_providers_args_parser = argparse.ArgumentParser(add_help=False)
        self.subparsers = self.parser.add_subparsers(
            title="The IP record provider you want to run this scanner against",
            dest="provider",
            required=True
        )

        self._init_common_args_parser()
        self._init_aws_parser()
        self._init_cloudflare_parser()

    def _init_common_args_parser(self):
        parser = self.common_providers_args_parser.add_argument_group('Scanner Arguments')
        parser.add_argument(
            '--flags',
            action='store',
            dest='nmap_flags',
            help='Arguments to pass to NMAP',
            default='-T4 --open --exclude-ports 25'
        )
        parser.add_argument(
            '-s',
            '--sleep',
            action='store',
            dest='sleep_time',
            type=int,
            help='Amount of time (in seconds) to wait before re-running scan',
            default=60
        )
        parser.add_argument(
            '--no-loop',
            dest='no_loop',
            default=False,
            action='store_true',
            help='Only run the scanner one time, then exit'
        )
        parser.add_argument(
            '--slack-web-hook',
            action='store',
            required=True,
            dest='slack_web_hook',
            help='Slack Web Hook URL'
        )
        parser.add_argument(
            '--slack-user',
            action='store',
            dest='slack_user',
            help='Slack User',
            default='nmap monitor'
        )
        parser.add_argument(
            '--slack-icon-emoji',
            action='store',
            help='Slack Icon Emoji',
            default=':nmap:'
        )

    def _init_cloudflare_parser(self):
        parser = self.subparsers.add_parser(
            name='cloudflare',
            parents=[self.common_providers_args_parser],
            help="Run scanner against Cloudflare DNS records"
        )

        parser.add_argument(
            '-z',
            '--zone',
            action='store',
            required=True,
            dest='cloudflare_zone',
            help='Cloudflare Zone'
        )
        parser.add_argument(
            '-t',
            '--token',
            action='store',
            required=True,
            dest='cloudflare_token',
            help='Cloudflare API Token'
        )
        parser.add_argument(
            '--dns-name-filter',
            action='store',
            dest='cloudflare_dns_name_filter',
            help='Filer DNS records by name'
        )

    def _init_aws_parser(self):
        parser = self.subparsers.add_parser(
            'aws',
            parents=[self.common_providers_args_parser],
            help='Run scanner against an Amazon Web Services EC2 agents'
        )

        aws_parser = parser.add_argument_group('Authentication modes')
        aws_auth_params = parser.add_argument_group('Authentication parameters')

        aws_auth_modes = aws_parser.add_mutually_exclusive_group(required=False)

        aws_auth_modes.add_argument(
            '-p',
            '--profile',
            dest='profile',
            default=None,
            help='Run with a named profile'
        )

        aws_auth_modes.add_argument(
            '--access-keys',
            action='store_true',
            dest='aws_access_keys',
            help='Run with access keys'
        )

        aws_auth_params.add_argument(
            '--access-key-id',
            action='store',
            default=None,
            dest='aws_access_key_id',
            help='AWS Access Key ID'
        )

        aws_auth_params.add_argument(
            '--secret-access-key',
            action='store',
            default=None,
            dest='aws_secret_access_key',
            help='AWS Secret Access Key'
        )

        aws_auth_params.add_argument(
            '--session-token',
            action='store',
            default=None,
            dest='aws_session_token',
            help='AWS Session Token'
        )

    def parse_args(self, args=None) -> dict:
        args = self.parser.parse_args(args)
        v = vars(args)
        # AWS
        if v.get('provider') == 'aws':
            if v.get('aws_access_keys') and not (v.get('aws_access_key_id') or v.get('aws_secret_access_key')):
                self.parser.error(
                    'When running with --access-keys, you must provide an Access Key ID and Secret Access Key.'
                )
        return args
