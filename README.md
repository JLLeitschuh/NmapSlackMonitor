# Nmap Slack Monitor

Monitor your network infrastructure using [Nmap](https://nmap.org/) and get Slack notifications when things change.

This script was originally inspired by [Jerry Gamblin's bash script](https://jerrygamblin.com/2017/09/04/network-monitoring-with-slack-alerting/).

## Data Sources

Jerry's original script took an IP range to scan. However, the reality of modern cloud-first infrastructure is that your
public facing network can change dynamically and may not be constrained by fixed IP blocks.

The goal of this script is to enable you to pull down your IP records using the APIs from various sources.

| Service    | Support              |
|------------|----------------------|
| Cloudflare | :+1: Supported |
| AWS        | :warning: Planned    |
