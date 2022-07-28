import os
from configobj import ConfigObj
from config import conf as data
from database.DBparser import DBparser
from ipaddress import IPv6Network


class DhcpV6:

    def __init__(self):
        self.dhcp_parser = DBparser()

    def dhcp_generator_file(self):
        '''
        cria os arquivos dhcp, com base nas informações do param6.conf
        '''
        # lista de nome de todas as redes inseridas no dhcp_param.conf
        config = ConfigObj(data.config6)
        # cria os arquivos correspondetes, se não existirem
        for param_type in config['networks-dhcp']:
            for vlanid in config['networks-dhcp'][param_type]:
                self.__create_file_dhcp_if_no_exist(vlanid)

    def dhcp_generator_conf(self):
        # delete os arquivos atuais
        self.__delete_all_dhcp_files()
        # gera novos arquivos
        self.dhcp_generator_file()

        file_param = ConfigObj(data.config6)
        file_param_conf_dhcp = file_param['conf-dhcp']

        for network_type in file_param['networks-dhcp']:
            networks_address: list = []

            for vid in file_param['networks-dhcp'][network_type]:
                network_aux = file_param['networks-dhcp'][network_type][vid]
                # testa se é string ou lista
                if type(network_aux) == str:
                    networks_address.append(network_aux)
                else:
                    networks_address = network_aux
                control_share_1 = True
                control_share_2 = len(networks_address) - 1
                cont = 0
                for network_addr in networks_address:
                    all_ips_addr: list = []
                    net = IPv6Network(network_addr)
                    for addr in net:
                        # todos os IPs
                        cont+=1
                        if cont > 4096:
                            break
                        all_ips_addr.append(addr)

                    network_address_dhcp = str(net.network_address)
                    min_range_address_dhcp = int(file_param_conf_dhcp[network_type]['reserved_address'])
                    default_lease_time = file_param_conf_dhcp[network_type]['default-lease-time']
                    max_lease_time = file_param_conf_dhcp[network_type]['max-lease-time']
                    deny_unknown_clients = int(file_param_conf_dhcp[network_type]['deny-unknown-clients'])
                    prefixlen = net.prefixlen

                    # caminho do arquivo
                    path = data.dhcp_dir6 + "dhcpv6." + vid

                    with open(path, 'a') as file:
                        print(f"\nRede: {vid}\n")
                        l1 = f"subnet6 {network_address_dhcp}/{prefixlen}" + "{"
                        l5 = f"\n     default-lease-time {default_lease_time};"
                        l6 = f"\n     max-lease-time {max_lease_time};"
                        if min_range_address_dhcp != 0:
                            l7 = f"\n     range6 {all_ips_addr[min_range_address_dhcp]} {all_ips_addr[-2]};"
                        else:
                            l7 = ''

                        if deny_unknown_clients == 1:
                            l9 = f"\n     deny unknown-clients;"
                        else:
                            l9 = ''
                        lf = '\n\n'
                        linha = l1 + l5 + l6 + l7 + l9 + lf
                        if control_share_1:
                            file.write('shared-network ' + vid + ' {\n\n')
                            control_share_1 = False
                        file.write(linha)

                        print("\n" + linha + "\n")
                        all_ips = self.get_all_lines_dhcp_by_network(network_address_dhcp)
                        for l_ip in all_ips:
                            if l_ip == 'erro':
                                break
                            li = '     ' + l_ip
                            file.write(li)
                            print(li)

                        file.write("\n  }")
                        if control_share_2 == 0:
                            file.write("\n}")
                        control_share_2 -= 1

    def __create_file_dhcp_if_no_exist(self, vlan: str) -> bool:
        new_file = ''
        try:
            new_file = data.dhcp_dir6 + "dhcpv6." + vlan
            exist = os.path.exists(new_file)
        except TypeError:
            exist = True

        if exist is False:
            command = 'touch ' + new_file
            os.system(command)
        return True

    def __delete_all_dhcp_files(self):
        files = data.dhcp_dir6 + "dhcp*"
        command = 'rm -rf ' + files
        os.system(command)

    def get_all_lines_dhcp_by_network(self, network: str) -> list:
        # gera as linhas que irão para o arquivo DHCP.
        # Apenas as linhas que tiverem endereços MAC válidos
        # apenas linhas que tiverem com o status (id 4) vão pro DHCP
        # apenas linhas que contiverem IPv6
        #try:
        all_ips: list = []
        ips = self.dhcp_parser.get_ipv6_by_network(network)
        new_line = "\n"
        all_ips.append(new_line)

        for line in ips:
            ip = str(line).split('__')[0]
            name = str(line).split('__')[1]
            mac = str(line).split('__')[2]
            if ':' in mac:
                new_line = "host " + name + " { hardware ethernet " + mac + " ; fixed-address6 " + ip + " ; }\n"
                all_ips.append(new_line)
        #except IndexError:
            #all_ips = ['erro']
        return all_ips


class DHCPv6conf:

    def __init__(self):
        self.__create_dhcpv6_conf_if_no_exist()
        self.dhcpv6_conf_gen()

    def __create_dhcpv6_conf_if_no_exist(self) -> bool:
        new_file = ''
        try:
            new_file = data.dhcpv6_conf
            exist = os.path.exists(new_file)
        except TypeError:
            exist = True

        if exist is False:
            command = 'touch ' + new_file
            os.system(command)
        return True

    def dhcpv6_conf_gen(self):
        path = data.dhcpv6_conf
        config = ConfigObj(data.config6)
        dns_combo1 = str(config['server-dns']['combo1']).replace('[', '').replace(']', '').replace("'", "")
        log_facility = config['log']['dhcp']['facility']
        with open(path, 'w+') as file:
            header = "\n###################   CONFIGURACAO DHCPv6 UFSM  ##################################" \
                     "\n" \
                     "\nddns-update-style none;" \
                     f"\nlog-facility {log_facility};" \
                     f"\n" \
                     f"\n" \
                     "\nsubnet6 2804:0:4000:4::/64" \
                     f"\n"+"{" \
                     f"\n     option dhcp6.name-servers {dns_combo1};" \
                     "\n}\n\n"\

            includes_dhcpv6 = ''

            file.write(header)
            file.write(includes_dhcpv6)
            file.writelines(self.dhcpv6_includes())

    def dhcpv6_includes(self) -> list:
        command = 'ls ' + data.dhcp_dir6 + 'dhcpv6*'
        result_lines = os.popen(command)
        includes: list = []
        for line in result_lines.readlines():
            line = line.replace("\n", '')
            includes.append(f'include "{line}";\n')

        return includes



if '__main__' == __name__:
    #dhcp = DHCPv6conf()
    #dhcp.dhcpv6_conf_gen()

    dhcp2 = DhcpV6()
    dhcp2.dhcp_generator_conf()