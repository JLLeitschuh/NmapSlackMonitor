import datetime
import os
import time
from typing import Optional

from NmapSlackMonitor.aws import AwsAPI
from NmapSlackMonitor.cli_parser import ScannerArgumentParser
from NmapSlackMonitor.cloudflare import CloudFlareAPI
from NmapSlackMonitor.slack import SlackAPI
from NmapSlackMonitor.target_provider import TargetProvider

_TIME_STRING_FORMAT_ = "%Y-%m-%d %H:%M:%S"


def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0


def relative_symlink(src, dst):
    if os.path.dirname(src) != os.path.dirname(dst):
        raise Exception('src and dst must have the same base path')
    file_name = os.path.basename(src)
    os.symlink(file_name, dst)


def process_target(target: str, date_str: str, nmap_flags: str) -> Optional[str]:
    slack_message = None
    print()
    now = datetime.datetime.now()
    print(f'{now.strftime(_TIME_STRING_FORMAT_)} - starting {target}')

    curr_log = f'scans/scan-{target}-{date_str}.xml'
    prev_log = f'scans/scan-{target}-prev.xml'
    diff_log = f'scans/scan-{target}-diff.xml'

    os.system(f'nmap {nmap_flags} {target} -oX {curr_log} > /dev/null')

    # If there's a previous log, diff it
    if os.path.exists(prev_log):
        # Exclude the Nmap version and current date - the date always changes
        # Ndiff is written in python2 and so needs to run under python2
        ndiff_command = "$(which ndiff)"
        os.system(f'python2 {ndiff_command} {prev_log} {curr_log} | egrep -v "^(\+|-)N" > {diff_log}')
        if not is_file_empty(diff_log):
            print('Changes Detected, Sending to Slack.')
            open_ports = os.popen(f'nmap -sV {target} | grep open | grep -v "#" > openports.txt').read()
            open_ports_msg = f'Changes were detected on {target}. The following ports are now open: \n{open_ports}'
            print(open_ports_msg)
            # The message to be sent to slack
            slack_message = open_ports_msg

            # Set the current nmap log file to reflect the last date changed
            os.remove(prev_log)
            relative_symlink(curr_log, prev_log)
        else:
            # No changes so remove our current log
            print("No Changes Detected.")
            os.remove(curr_log)
        os.remove(diff_log)
    else:
        # Create the previous scan log
        relative_symlink(curr_log, prev_log)

    return slack_message


def run_from_cli():
    scanner_arg_parser = ScannerArgumentParser()
    args = scanner_arg_parser.parse_args()
    args = args.__dict__

    slack = SlackAPI(
        slack_web_hook=args.get('slack_web_hook'),
        slack_user=args.get('slack_user'),
        icon_emoji=args.get('slack_icon_emoji')
    )

    target_provider: TargetProvider
    if args.get('provider') == 'cloudflare':
        target_provider = CloudFlareAPI(
            zone=args.get('cloudflare_zone'),
            api_token=args.get('cloudflare_token'),
            name_filter=args.get('cloudflare_dns_name_filter')
        )
    elif args.get('provider') == 'aws':
        target_provider = AwsAPI.authenticate(
            profile=args.get('profile'),
            aws_access_key_id=args.get('aws_access_key_id'),
            aws_secret_access_key=args.get('aws_secret_access_key'),
            aws_session_token=args.get('aws_session_token')
        )
    targets = target_provider.get_ips()

    while True:
        start_time = datetime.datetime.now()

        date_str = start_time.strftime('%Y-%m-%d_%H-%M-%S')
        for target in targets:
            slack_message = process_target(target, date_str, args.get('nmap_flags'))
            if slack_message:
                slack.post_to_slack(slack_message)

        end_time = datetime.datetime.now()
        elapsed_seconds = end_time.second - start_time.second
        count = len(targets)
        print(
            f'{end_time.strftime(_TIME_STRING_FORMAT_)} - finished all {count} targets in {elapsed_seconds} second(s)'
        )

        time.sleep(args.get('sleep_time'))
