import argparse
import os
from time import sleep
from arpwatch import ManagerArpWatch
from dhcp import Dhcp, DHCPv4conf
from dns import Dns
from dhcpv6 import DhcpV6, DHCPv6conf
from dnsv6 import DnsV6


parser = argparse.ArgumentParser()

parser.add_argument("--run4", dest="run4", help="atualiza os arquivos ipv4, quando o banco muda", action='store_true')

parser.add_argument("--run6", dest="run6", help="atualiza os arquivos ipv6, quando o banco muda", action='store_true')

parser.add_argument("--startv4", dest="startv4", help="rodar sempre que uma NOVA REDE IPV4for adicionada", action='store_true')

parser.add_argument("--startv6", dest="startv6", help="rodar sempre que uma NOVA REDE IPV6 for adicionada", action='store_true')
# parser.add_argument("--dhcp", dest="dhcp", help="'update': sincroniza os dados do banco de dados IPAM com os arquivos DHCP ")

# parser.add_argument("--dns", dest="dns",help="'update': sincroniza os dados do banco de dados IPAM com os arquivos DNS ")

parser.add_argument("--arpwatch", dest="arpwatch", help="adiciona os endereços capturados pelo ARPWATCH ",
                    action='store_true')

parser.add_argument("--leases", dest="lease", help="comando mostra IP e MAC das leases atuais",
                    action='store_true')

args = parser.parse_args()

'''
O primeiro passo sempre é criar as redes no PHP IPAM.
Após criadas, as redes devem ser informadas no arquivo "param.conf"
'''

if (args.startv4):
    # popula o banco de dados e gera os arquivos DNS
    dns = Dns()

    # preenche o banco de dados com IPs e NOMES
    dns.ip_generator()
    sleep(1)

    # cria os arquivos DNS
    dns.dns_generator()
    sleep(1)

    # gera os arquivos DHCP
    dhcp = Dhcp()
    dhcp.dhcp_generator_conf()

    # gera o arquivo de configuração DHCP e adiciona os includes
    DHCPv4conf()

    #reinicia o serviço dhcp
    os.system("/etc/init.d/isc-dhcp-server restart")

if (args.startv6):
    # popula o banco de dados e gera os arquivos DNS
    dns = DnsV6()

    # preenche o banco de dados com IPs e NOMES
    dns.ip_generator()
    sleep(1)

    # cria os arquivos DNS
    dns.dns_generator()
    sleep(1)

    # gera os arquivos DHCP
    dhcp = DhcpV6()
    dhcp.dhcp_generator_conf()

    # gera o arquivo de configuração DHCP e adiciona os includes
    DHCPv6conf()

    #reinicia o serviço dhcp
    #os.system("/etc/init.d/isc-dhcp-server restart")

elif (args.run4):

    # gera os arquivos DHCP
    dhcp = Dhcp()
    dhcp.dhcp_generator_conf()

    # gera o arquivo de configuração DHCP e adiciona os includes
    DHCPv4conf()

    #reinicia o serviço dhcp
    os.system("/etc/init.d/isc-dhcp-server restart")

elif (args.run6):

    # gera os arquivos DHCP
    dhcp = DhcpV6()
    dhcp.dhcp_generator_conf()

    # gera o arquivo de configuração DHCP e adiciona os includes
    DHCPv6conf()

    #reinicia o serviço dhcp
    os.system("/etc/init.d/isc-dhcp-server restart")


elif (args.arpwatch):
    ManagerArpWatch()

else:
    print("\nDigite: 'ipam -h' para ver as opções\n ")
