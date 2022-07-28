import os
import random
from ipaddress import IPv4Network
from configobj import ConfigObj
from config import conf as data
from database.DBparser import DBparser
from dnsv6 import DnsV6


class Dns:

    def dns_generator(self):
        '''
        cria os arquivos dns, com base nas informações do arquivo "param.conf"
        '''
        # deleta os arquivos antigos, antes de gerar outros
        self.__delete_all_dns_files()
        config = ConfigObj(data.config)
        # cria os arquivos correspondetes, se não existirem
        networks_address: list = []
        for domain in config['networks-dns']:
            network_aux = config['networks-dns'][domain]
            # testa se é string ou lista
            if type(network_aux) == str:
                networks_address.append(network_aux)
            else:
                networks_address = network_aux

            for network in networks_address:
                print(network)
                self.__create_file_dns_if_no_exist(network)

    def dns_ips_names(self, network):
        all_ips: list = []
        dns_paser = DBparser()
        ips = dns_paser.get_ip_by_network(str(network))
        new_line = "\n"
        all_ips.append(new_line)
        name_net = str(network).split('.')[0] + '.' + str(network).split('.')[1] + '.' + str(network).split('.')[2]
        file_name = data.dns_dir + 'dbrev_' + name_net

        for line in ips:
            if 'NaN' not in line:
                ip = str(line).split('__')[0].split('.')[-1]
                ip_full = str(line).split('__')[0]
                if ip == '0':
                    name_net = str(ip_full).split('.')[0] + '.' + str(ip_full).split('.')[1] + '.' + \
                               str(ip_full).split('.')[2]
                    file_name = data.dns_dir + 'dbrev_' + name_net

                with open(file_name, 'a+') as file:
                    name = str(line).split('__')[1]
                    if ip != '0' and ip != '255' and ip != '1':
                        new_line = ip + f"       IN      PTR     {name}. \n"
                        file.write(new_line)

    def ip_generator(self):
        '''
        cadastra os IPs e descrição (nomes) se ainda não estiverem cadastrado
        :param subnet: 192.168.2.0/24
        :return:
        '''
        # todas as redes inseridas no param.conf
        config = ConfigObj(data.config)
        # cria os arquivos correspondetes, se não existirem
        networks_address: list = []
        for domain in config['networks-dns']:
            network_aux = config['networks-dns'][domain]
            # testa se é string ou lista
            if type(network_aux) == str:
                networks_address.append(network_aux)
            else:
                networks_address = network_aux

            for subnet in networks_address:
                network_gen = IPv4Network(subnet)
                network_addr = network_gen.network_address
                broadcast = network_gen.broadcast_address
                all_ips_gen: list = []
                for addr in network_gen:
                    if addr != network_addr and addr != broadcast:
                        ip = str(addr)
                        last_oct = ip.split('.')[-1]
                        # if last_oct != '0' and last_oct != '255' and ip != '1':
                        all_ips_gen.append(ip)

                dp = DBparser()
                dp.no_dhcp_null()
                all = dp.get_ip_by_network(subnet)
                all_ips_db: list = []
                # pega todos os ips cadastrados no banco
                for line_ipam in all:
                    # testa se o MAC é válido ou é um número aleatório
                    all_ips_db.append(str(line_ipam).split('__')[0].strip())

                # cadastra todos os que ainda não estão no banco
                for ip_gen in all_ips_gen:
                    if ip_gen not in all_ips_db:
                        net_str = str(network_addr)
                        hostname = str(ip_gen).replace('.', '-') + '.' + domain
                        dp.insert_ipaddresses(net_str, ip_gen, hostname)

    def serial_number(self, ip: str):
        dp = DBparser()
        last_edit = dp.get_last_edit_ip(ip)
        fin = random.randint(0, 99)
        if fin < 10:
            fin = '0' + str(fin)
        else:
            fin = str(fin)
        serial_number = last_edit.replace('-', '').replace(':', '').replace(' ', '')[:-6] + fin

        return serial_number

    def headers(self, net: str) -> str:

        info = IPv4Network(net)
        netmask = info.netmask
        addr_test = str(info.broadcast_address)[:-1] + '3'
        qtd_hosts = 0
        for _ in IPv4Network(net):
            qtd_hosts += 1

        qtd_subnets = int(qtd_hosts / 256)
        qtd_hosts = int(qtd_hosts - 2)
        serial_number = self.serial_number(addr_test)
        header = "$ttl          86400" \
                 "\n;========================================================" \
                 "\n; UFSM-CPD-DIVISAO DE SUPORTE" \
                 "\n;" \
                 "\n;" \
                 f"\n; Netmask: {netmask}" \
                 f"\n; Subnets: {qtd_subnets}" \
                 f"\n; Pontos : {qtd_hosts}" \
                 "\n;========================================================\n" \
                 "\n@       IN      SOA     esfinge.ufsm.br. dnsadm.ufsm.br. (" \
                 f"\n                        {serial_number} ; Serial Number" \
                 "\n                        10800	 ; Refresh 	   3 hours" \
                 "\n                        1800	 ; Retry	   30 minutes" \
                 "\n                        2592000	 ; Expire	   30 days" \
                 "\n                        86400 )	 ; Minimum	   1 day" \
                 "\n" \
                 "\n;========================================================" \
                 "\n; servidores de nomes e de mail" \
                 "\n;========================================================" \
                 "\n    IN	NS	esfinge.ufsm.br." \
                 "\n    IN	NS	bagda.ufsm.br." \
                 "\n    IN	NS	ns3.ufsm.br." \
                 "\n    IN	NS	ns4.ufsm.br." \
                 "\n;========================================================\n"
        return header

    def __create_file_dns_if_no_exist(self, network: str) -> bool:
        # se a rede for maior (23,22, etc) do que um /24, é necessário criar mais de um arquivo
        prefixlen = int(IPv4Network(network).prefixlen)
        if prefixlen <=24:
            subnets = IPv4Network(network).subnets(new_prefix=24)
        else:
            subnets = IPv4Network(network).subnets(new_prefix=prefixlen)
        for sub in subnets:
            subnet = str(sub.network_address)
            ip = subnet[:len(subnet) - len(subnet.split('.').pop())][:-1]
            new_file = data.dns_dir + "dbrev_" + ip
            exist = os.path.exists(new_file)

            # abre o arquivo e adiciona o cabeçalho correspondente e linhas de IP
            if exist is False:
                command = 'touch ' + new_file
                os.system(command)
                header = self.headers(network)

                with open(new_file, 'a') as file:
                    file.write(header)
                    file.write('\n')

        self.dns_ips_names(str(network))
        return True

    def __delete_all_dns_files(self):
        files = data.dns_dir + "dbrev*"
        command = 'rm -rf ' + files
        os.system(command)


if '__main__' == __name__:
    dns = DnsV6()
    dns.ip_generator()
    #dns.dns_generator()
    #print(dns.serial_number('192.168.76.7'))
