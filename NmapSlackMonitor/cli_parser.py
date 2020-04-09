import argparse


class ScannerArgumentParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Run a regular NMAP Scan of your Network and post changes to Slack'
        )
        self.common_providers_args_parser = argparse.ArgumentParser(add_help=False)
        self.subparsers = self.parser.add_subparsers(
            title="The IP record provider you want to run this scanner against",
            dest="provider"
        )

        self._init_common_args_parser()
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

    def parse_args(self, args=None) -> dict:
        args = self.parser.parse_args(args)
        return args
