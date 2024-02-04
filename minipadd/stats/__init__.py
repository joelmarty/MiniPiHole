import locale
import os
import socket
import time
from dataclasses import dataclass
from typing import Dict, Any

import psutil
import requests

from minipadd.config import PiHoleConfig


@dataclass
class SystemStats:
    hostname: str
    ip: str
    uptime: int
    cpu_temp: int
    cpu_usage: float
    load: tuple[float, float, float]


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
    status: str
    last_update: Dict[str, Any]


def ftl_atoi(value: str) -> int:
    return int(value.replace(',', ''))


def ftl_atof(value: str) -> float:
    return float(value.replace(',', ''))


class Stats:
    def __init__(self, pihole_conf: PiHoleConfig):
        self.pihole_iface = pihole_conf.pihole_iface
        self.pihole_token = pihole_conf.pihole_token
        self.pihole_api_host = pihole_conf.pihole_api_host

    def get_system_stats(self) -> SystemStats:
        # get uptime
        uptime = time.clock_gettime(time.CLOCK_BOOTTIME)

        # cpu temp
        temps = psutil.sensors_temperatures().get('cpu_thermal', [])
        temp_val = temps[0].current if len(temps) > 0 else 0

        # pihole interface
        addr = next(filter(lambda i: i.family == socket.AF_INET, psutil.net_if_addrs().get(self.pihole_iface, [])))

        return SystemStats(
            uptime=int(uptime),
            cpu_temp=int(temp_val),
            cpu_usage=psutil.cpu_percent(),
            load=psutil.getloadavg(),
            hostname=os.uname().nodename,
            ip=addr.address)

    def get_ftl_stats(self) -> FtlStats:
        resp = requests.get(f'http://{self.pihole_api_host}/admin/api.php',
                            params={'summary': True, 'auth': self.pihole_token})
        stats = resp.json()
        return FtlStats(
            domains_being_blocked=ftl_atoi(stats.get('domains_being_blocked', '0')),
            dns_queries_today=ftl_atoi(stats.get('dns_queries_today', 0)),
            ads_blocked_today=ftl_atoi(stats.get('ads_blocked_today', 0)),
            ads_percentage_today=ftl_atof(stats.get('ads_percentage_today', 0)) / 100,
            unique_domains=ftl_atoi(stats.get('unique_domains', 0)),
            queries_forwarded=ftl_atoi(stats.get('queries_forwarded', 0)),
            queries_cached=ftl_atoi(stats.get('queries_cached', 0)),
            clients_ever_seen=ftl_atoi(stats.get('clients_ever_seen', 0)),
            unique_clients=ftl_atoi(stats.get('unique_clients', 0)),
            dns_queries_all_types=ftl_atoi(stats.get('dns_queries_all_types', 0)),
            dns_queries_all_replies=ftl_atoi(stats.get('dns_queries_all_replies', 0)),
            status=stats.get('status', 'disabled'),
            last_update=stats.get('gravity_last_updated', {}).get('absolute', 0))
