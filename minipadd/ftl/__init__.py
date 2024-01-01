from dataclasses import dataclass
from typing import Dict, Any
from envfileparser import get_env_from_file
import requests


@dataclass
class FtlStats:
    domains_being_blocked: int
    dns_queries_today: int
    ads_blocked_today: int
    ads_percentage_today: float
    unique_domains: int
    queries_forwarded: int
    queries_cached: int
    clients_ever_seen: int
    unique_clients: int
    dns_queries_all_types: int
    dns_queries_all_replies: int
    status: bool
    last_update: Dict[str, Any]


def get_pihole_token(pihole_dir: str) -> str:
    """
    Retrieve the pihole token from the setup configuration file (setupVars.conf).
    This app must have access to /etc/pihole, so if running in a container,
    the app must have access to the pihole volume.

    :return: the API token
    """
    return get_env_from_file('WEBPASSWORD', file_path=f'{pihole_dir}/setupVars.conf')


def get_stats(host: str, token: str) -> FtlStats:
    resp = requests.get(f'http://{host}/admin/api.php', params={'summary': True, 'auth': token})
    stats = resp.json()
    return FtlStats(
        domains_being_blocked=stats.get('domains_being_blocked', 0),
        dns_queries_today=stats.get('dns_queries_today', 0),
        ads_blocked_today=stats.get('ads_blocked_today', 0),
        ads_percentage_today=stats.get('ads_percentage_today', 0),
        unique_domains=stats.get('unique_domains', 0),
        queries_forwarded=stats.get('queries_forwarded', 0),
        queries_cached=stats.get('queries_cached', 0),
        clients_ever_seen=stats.get('clients_ever_seen', 0),
        unique_clients=stats.get('unique_clients', 0),
        dns_queries_all_types=stats.get('dns_queries_all_types', 0),
        dns_queries_all_replies=stats.get('dns_queries_all_replies', 0),
        status=stats.get('status', False),
        last_update=stats.get('gravity_last_updated', {}).get('absolute', 0))
