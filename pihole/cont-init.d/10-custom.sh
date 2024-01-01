#!/command/with-contenv bash
# shellcheck shell=bash

set -e

# avoid port conflicts with resin-dns
# https://docs.pi-hole.net/ftldns/interfaces/
# these steps must be at runtime because /etc/dnsmasq.d is a user volume
echo "bind-interfaces" > /etc/dnsmasq.d/90-resin-dns.conf
echo "except-interface=resin-dns" >> /etc/dnsmasq.d/90-resin-dns.conf
