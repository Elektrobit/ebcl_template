#!/bin/bash

# === 1. DNS Discovery ===
ip_v4_dns=$(awk '/^nameserver/ && $2 ~ /^[0-9.]+$/ {print $2; exit}' /etc/resolv.conf)

# Detect interface for IPv6 link-local DNS (e.g., FritzBox)
iface=$(ip -6 route | awk '/^default/ {print $5; exit}')
ip_v6_dns="fe80::4a5d:35ff:feee:e73d%$iface"  # Adjust if FritzBox DNS changes

echo "IPv4 DNS: $ip_v4_dns"
echo "IPv6 DNS: $ip_v6_dns"

# === 2. Prime DNS (optional: helps on fresh boots) ===
host ipv6.google.com > /dev/null 2>&1
sleep 1

# === 3. Get Tesla Final Host ===
FINAL_HOST=$(host www.tesla.com | awk '/alias/ {print $NF}' | tail -n1)
[ -z "$FINAL_HOST" ] && FINAL_HOST="www.tesla.com"

# === 4. Resolve Tesla IPs ===
TESLA_IPV4=$(host "$FINAL_HOST" | awk '/has address/ {print $NF}' | head -n1)
TESLA_IPV6=$(host "$FINAL_HOST" | awk '/has IPv6 address/ {print $NF}' | head -n1)

echo "Tesla IPv4: $TESLA_IPV4"
echo "Tesla IPv6: $TESLA_IPV6"

# === 5. Flush old rules ===
iptables -F
ip6tables -F
iptables -P OUTPUT DROP
iptables -P INPUT DROP
ip6tables -P OUTPUT DROP
ip6tables -P INPUT DROP

# === 6. Allow localhost ===
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT
ip6tables -A INPUT -i lo -j ACCEPT

# === 7. DNS Rules ===
# IPv4 DNS
iptables -A OUTPUT -p udp -d $ip_v4_dns --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp -d $ip_v4_dns --dport 53 -j ACCEPT
iptables -A INPUT  -p udp -s $ip_v4_dns --sport 53 -j ACCEPT
iptables -A INPUT  -p tcp -s $ip_v4_dns --sport 53 -j ACCEPT

# IPv6 DNS
ip6tables -A OUTPUT -p udp -d ${ip_v6_dns} --dport 53 -j ACCEPT
ip6tables -A OUTPUT -p tcp -d ${ip_v6_dns} --dport 53 -j ACCEPT
ip6tables -A INPUT  -p udp -s ${ip_v6_dns} --sport 53 -j ACCEPT
ip6tables -A INPUT  -p tcp -s ${ip_v6_dns} --sport 53 -j ACCEPT

# === 8. Allow ESTABLISHED/RELATED Connections ===
iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
ip6tables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# === 9. Tesla IPv4 Access ===
iptables -A OUTPUT -d $TESLA_IPV4 -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -d $TESLA_IPV4 -p tcp --dport 443 -j ACCEPT
iptables -A OUTPUT -d $TESLA_IPV4 -p icmp -j ACCEPT
iptables -A INPUT  -s $TESLA_IPV4 -p icmp -j ACCEPT

# === 10. Tesla IPv6 Access (HTTPS + Ping Only) ===
ip6tables -A OUTPUT -d $TESLA_IPV6 -p tcp --dport 443 -j ACCEPT
ip6tables -A OUTPUT -d $TESLA_IPV6 -p icmpv6 --icmpv6-type echo-request -j ACCEPT
ip6tables -A INPUT  -s $TESLA_IPV6 -p icmpv6 --icmpv6-type echo-reply -j ACCEPT

# === 11. Block ALL other ICMPv6 echo requests ===
ip6tables -A INPUT  -p icmpv6 --icmpv6-type echo-request -j REJECT
ip6tables -A OUTPUT -p icmpv6 --icmpv6-type echo-request -j REJECT

# === Done ===
echo "[+] Firewall rules applied. Only Tesla (IPv4 & IPv6) allowed."
