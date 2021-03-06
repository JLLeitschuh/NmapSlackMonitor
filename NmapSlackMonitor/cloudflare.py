from dataclasses import dataclass
from typing import Optional, List, Iterable, Tuple

import requests

from NmapSlackMonitor.target_provider import TargetProvider


@dataclass(frozen=True)
class CloudFlareAPI(TargetProvider):
    zone: str
    api_token: str
    name_filter: Optional[str]

    def _get_dns_raw(self, page) -> dict:
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            url=f'https://api.cloudflare.com/client/v4/zones/{self.zone}/dns_records?type=A&match=all&per_page=50&page={page}',
            headers=headers
        )
        return response.json()

    def _process_results(self, raw_results: dict) -> Iterable[Tuple[str, str]]:
        for result in raw_results['result']:
            if self.name_filter not in result['name']:
                continue
            yield result['content'], result['name']

    def get_ips(self) -> List[Tuple[str, Optional[str]]]:
        ips: List[Tuple[str, str]] = []
        page_number = 0
        while True:
            page_number += 1
            raw_results = self._get_dns_raw(page_number)
            ips.extend(self._process_results(raw_results))
            total_pages = raw_results['result_info']['total_pages']

            if page_number >= total_pages:
                break
        return ips
