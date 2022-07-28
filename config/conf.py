import os

script_dir = os.path.dirname(__file__)
dhcp_dir = os.path.join(script_dir, '../files/dhcpv4/')
dhcpv4_conf = os.path.join(script_dir, '../files/dhcpv4.conf')
dhcpv6_conf = os.path.join(script_dir, '../files/dhcpv6.conf')
dns_dir = os.path.join(script_dir, '../files/dnsv4/')
dhcp_dir6 = os.path.join(script_dir, '../files/dhcpv6/')
dns_dir6 = os.path.join(script_dir, '../files/dnsv6/')
config = os.path.join(script_dir, 'param.conf')
config6 = os.path.join(script_dir, 'param6.conf')
db_name = "phpipam"
db_pass = "[senha]"
db_host = "[endereço banco]"
db_user = "[ueser banco]"