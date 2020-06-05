from typing import List, Optional, Tuple


class TargetProvider:

    def get_ips(self) -> List[Tuple[str, Optional[str]]]:
        """Extract the DNS records to be scanned."""
        pass
