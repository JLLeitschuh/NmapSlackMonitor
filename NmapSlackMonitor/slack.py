from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class SlackAPI:
    slack_web_hook: str
    slack_user: str = "nmap monitor"
    icon_emoji: str = ":nmap:"

    def post_to_slack(self, text):
        payload = {
            'username': self.slack_user,
            'icon_emoji': self.icon_emoji,
            'text': text
        }
        requests.post(
            url=self.slack_web_hook,
            json=payload
        )
