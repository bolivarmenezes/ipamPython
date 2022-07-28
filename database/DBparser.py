from database.DBphpipam import Dbphpipam
from tools import Tools


class DBparser:

    def __init__(self):
        self.db = Dbphpipam()

    def dhcp_generator_conf(self) -> list:
        networks = self.db.db_networks()
        return networks

    def get_all_network_name(self) -> list:
        all_names = list(set(self.db.get_all_network_name()))
        return all_names

    def get_all_network_vid(self) -> list:
        all_vids = list(set(self.db.get_all_network_vid()))
        return all_vids

    def get_ip_by_network(self, network: str) -> list:
        if '/' in network:
            network = network.split('/')[0]
        # converte a rede para inteiro antes de buscar no banco
        network = Tools.convert_ip_to_int(network)
        all_ips = self.db.get_ip_by_network(network)
        return all_ips

    def get_ipv6_by_network(self, network: str) -> list:
        if '/' in network:
            network = network.split('/')[0]
        # converte a rede para inteiro antes de buscar no banco
        network = Tools.convert_ipv6_to_int(network)
        all_ips = self.db.get_ipv6_by_network(network)
        return all_ips

    def get_network_by_ip(self, ip: str) -> str:
        network: str = ''
        ip = Tools.convert_ip_to_int(ip)
        print(ip)
        # self.db.get_net
        return network

    def get_last_edit_ip(self, ip: str) -> str:
        # pega a rede do ip correspondente, e busca o último editado (dentro da rede dele)
        id_network = self.db.get_network_id_by_ip(ip)
        last_edit = str(self.db.get_last_edit_ip(id_network))
        return last_edit

    def get_last_edit_ipv6(self, ip: str) -> str:
        # pega a rede do ip correspondente, e busca o último editado (dentro da rede dele)
        id_network = self.db.get_network_id_by_ipv6(ip)
        last_edit = str(self.db.get_last_edit_ip(id_network))
        return last_edit

    # para garantir que não há dhcp vazio
    def no_dhcp_null(self):
        self.db.no_dhcp_null()
        return 0

    def insert_ipaddresses(self, network: str, ip_addr: str, hostname: str, mac: str = 'NULL',
                           is_gateway: int = 0,
                           description: str = 'NULL', state: int = 1):
        # se o MAC for NULL, gera um número aleatório
        # state = 1 para ficar offline por default, ou seja, livre para uso
        mac = Tools.random_number()

        # busca o id da rede no banco
        subnetId = self.db.get_id_net_by_network(network)
        # converte o ip para inteiro
        ip_addr = Tools.convert_ip_to_int(ip_addr)
        self.db.insert_ipaddresses(subnetId, ip_addr, hostname, mac, is_gateway, description, state)

    def insert_ipaddressesv6(self, network: str, ip_addr: str, hostname: str, mac: str = 'NULL',
                           is_gateway: int = 0,
                           description: str = 'NULL', state: int = 1):
        # se o MAC for NULL, gera um número aleatório
        # state = 1 para ficar offline por default, ou seja, livre para uso
        mac = Tools.random_number()

        # busca o id da rede no banco
        subnetId = self.db.get_id_net_by_networkv6(network)
        # converte o ip para inteiro
        ip_addr = Tools.convert_ipv6_to_int(ip_addr)
        self.db.insert_ipaddresses(subnetId, ip_addr, hostname, mac, is_gateway, description, state)

if __name__ == '__main__':
    dp = DBparser()
    dp.get_last_edit_ip('192.168.77.245')
    # dp.get_network_by_ip('200.18.72.27')
    # all_net = dp.get_ip_by_network('192.168.2.0')
    # print(all_net)
    # dp.get_last_edit_ip('200.18.72.251')
