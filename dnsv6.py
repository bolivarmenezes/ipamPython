import os
import random
from ipaddress import IPv6Network
from configobj import ConfigObj
from config import conf as data
from database.DBparser import DBparser


class DnsV6:

    def dns_generator(self):
        '''
        cria os arquivos dns, com base nas informações do arquivo "param.conf"
        '''
        # deleta os arquivos antigos, antes de gerar outros
        self.__delete_all_dns_files()
        config = ConfigObj(data.config6)
        # cria os arquivos correspondetes, se não existirem
        networkL:list =[]
        for domain in config['networks-dns']:
            # testa se é string ou lista
            if type(config['networks-dns'][domain]) == str:
                networkL.append(config['networks-dns'][domain])
            else:
                networkL = config['networks-dns'][domain]

            for network in networkL:
                self.__create_file_dns_if_no_exist(network)

    def dns_ips_names(self, network):
        all_ips: list = []
        dns_paser = DBparser()
        ips = dns_paser.get_ipv6_by_network(str(network))
        new_line = "\n"
        all_ips.append(new_line)
        address_expanded = IPv6Network(network).network_address.exploded
        name_new_file = "dbrev_" + ("_".join(address_expanded.split(':')[:-4]))
        file_name = data.dns_dir6 + name_new_file

        for line in ips:
            if 'NaN' not in line:
                ip = str(line).split('__')[0].split('.')[-1]
                ip_full = str(line).split('__')[0]
                if ip == '0':
                    name_net = str(ip_full).split('.')[0] + '.' + str(ip_full).split('.')[1] + '.' + \
                               str(ip_full).split('.')[2]
                    file_name = data.dns_dir6 + 'dbrev_' + name_net

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
        config = ConfigObj(data.config6)
        # cria os arquivos correspondetes, se não existirem
        networks_address:list = []
        for domain in config['networks-dns']:
            network_aux = config['networks-dns'][domain]
            # testa se é string ou lista
            if type(network_aux) == str:
                networks_address.append(network_aux)
            else:
                networks_address = network_aux
            for subnet in networks_address:
                network_gen = IPv6Network(subnet)
                network_addr = network_gen.network_address
                all_ips_gen: list = []
                count = 1
                for addr in network_gen:
                    if addr != network_addr:
                        if count < 4096:
                            ip = str(addr)
                            all_ips_gen.append(ip)
                            count += 1
                        else:
                            break

                dp = DBparser()
                dp.no_dhcp_null()
                all = dp.get_ipv6_by_network(subnet)
                all_ips_db: list = []
                # pega todos os ips cadastrados no banco
                for line_ipam in all:
                    # testa se o MAC é válido ou é um número aleatório
                    all_ips_db.append(str(line_ipam).split('__')[0].strip())

                # cadastra todos os que ainda não estão no banco
                for ip_gen in all_ips_gen:
                    if ip_gen not in all_ips_db:
                        net_str = str(network_addr)
                        address_expanded = IPv6Network(ip_gen).network_address.exploded.replace('0000','0')
                        address_expanded = address_expanded.replace(':000','-')
                        address_expanded = address_expanded.replace(':00', '-')
                        address_expanded = address_expanded.replace(":","-")
                        address_expanded_list = address_expanded.split('-')
                        full_address = ''
                        for address in address_expanded_list:
                            if address[0] == '0' and address!='0':
                                address = address[1:]
                            full_address+= address+'-'


                        hostname = full_address[:-1] + '.' + domain
                        dp.insert_ipaddressesv6(net_str, ip_gen, hostname)

    def serial_number(self, ip: str):
        dp = DBparser()
        last_edit = dp.get_last_edit_ipv6(ip)
        fin = random.randint(0, 99)
        if fin < 10:
            fin = '0' + str(fin)
        else:
            fin = str(fin)
        serial_number = last_edit.replace('-', '').replace(':', '').replace(' ', '')[:-6] + fin

        return serial_number

    def headers(self, net: str) -> str:
        info = IPv6Network(net)
        prefix = info.prefixlen
        host_test = info.hosts()
        first_ip = 'NaN'
        #network = info.network_address.reverse_pointer
        for host_test_last_modify in host_test:
            first_ip = host_test_last_modify
            break
        if first_ip != 'NaN':
            #origin = network
            #host_test_last_modify = first_ip
            serial_number = self.serial_number(str(host_test_last_modify))
            header = ";==========================================================================" \
                     "\n; UFSM-CPD-DIVISAO DE SUPORTE" \
                     "\n;" \
                     "\n;" \
                     f"\n; Netmask: {prefix}" \
                     "\n;==========================================================================\n" \
                     "\n$ttl          3600" \
                     "\n8.3.f.1.4.0.8.2.ip6.arpa.       IN      SOA     esfinge.ufsm.br. dnsadm.ufsm.br. (" \
                     f"\n                        {serial_number} ; Serial Number" \
                     "\n                        10800	 ; Refresh 	   3 hours" \
                     "\n                        1800	 ; Retry	   30 minutes" \
                     "\n                        2592000	 ; Expire	   30 days" \
                     "\n                        86400 )	 ; Minimum	   1 day" \
                     "\n" \
                     "\n;==========================================================================" \
                     "\n; servidores de nomes e de mail" \
                     "\n;==========================================================================" \
                     "\n8.3.f.1.4.0.8.2.ip6.arpa.       IN      NS      esfinge.ufsm.br." \
                     "\n8.3.f.1.4.0.8.2.ip6.arpa.       IN      NS      bagda.ufsm.br." \
                     "\n8.3.f.1.4.0.8.2.ip6.arpa.       IN      NS      pampa.tche.br." \
                     "\n;==========================================================================\n"
        return header

    def __create_file_dns_if_no_exist(self, network: str) -> bool:
        address_expanded = IPv6Network(network).network_address.exploded
        name_new_file = "dbrev_"+("_".join(address_expanded.split(':')[:-4]))
        '''
            cria um nome para o arquivo de reverso
        '''
        new_file = data.dns_dir6 + name_new_file
        print(new_file)
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
        files = data.dns_dir6 + "dbrev*"
        command = 'rm -rf ' + files
        os.system(command)


if '__main__' == __name__:
    dns = DnsV6()

    #dns.dns_generator()
    dns.ip_generator()