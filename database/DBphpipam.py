import datetime as datetime
from database.DBConnect import Connect
from tools import Tools
from datetime import datetime


class Dbphpipam:

    def __init__(self):
        conn = Connect()
        self.conn = conn.conn()

    def db_networks(self):
        cursor = self.conn.cursor(buffered=True)
        query = "select INET_NTOA(subnet), mask, description from subnets;"
        cursor.execute(query)
        networks: list = []
        for (subnet, mask, description) in cursor:
            networks.append(str(description) + '__' + str(subnet) + '/' + str(mask))
        return networks

    def get_all_network_name(self) -> list:
        cursor = self.conn.cursor(buffered=True)
        query = "select description from subnets;"
        cursor.execute(query)
        response: list = []
        for name in cursor:
            response.append(name[0])
        return response

    def get_all_network_vid(self) -> list:
        cursor = self.conn.cursor(buffered=True)
        query = "select vlanId from subnets;"
        cursor.execute(query)
        response: list = []
        for name in cursor:
            response.append(name[0])
        return response

    def get_id_net_by_ip(self, ip: str) -> int:
        cursor = self.conn.cursor(buffered=True)
        query = "select INET_NTOA(ip_addr), subnetId from ipaddresses;"
        cursor.execute(query)
        for (ip_banco, subnetId) in cursor:
            ip_banco = str(ip_banco).strip()
            if ip == ip_banco:
                return int(subnetId)
        return 0

    def get_id_net_by_network(self, network) -> int:
        # se tiver no formato normal ('192.168.1.0'), passa para interiro
        try:
            if '.' in network:
                network = Tools.convert_ip_to_int(network)
        except:
            pass
        cursor = self.conn.cursor(buffered=True)
        query = f"select id from subnets where subnet = {network};"
        cursor.execute(query)
        for id in cursor:
            return int(id[0])
        return 0

    def get_id_net_by_networkv6(self, network) -> int:
        try:
            if ':' in network:
                network = Tools.convert_ipv6_to_int(network)
        except:
            pass
        cursor = self.conn.cursor(buffered=True)
        query = f"select id from subnets where subnet = {network};"
        cursor.execute(query)
        for id in cursor:
            return int(id[0])
        return 0

    def get_ip_by_network(self, network) -> list:
        id_net = self.get_id_net_by_network(network)
        if id_net != 0:
            cursor = self.conn.cursor(buffered=True)
            query = f"select INET_NTOA(ip_addr), hostname, mac from ipaddresses where subnetId = {id_net} and state=4;"
            cursor.execute(query)
            response: list = []
            for (ip_addr, hostname, mac) in cursor:
                line = str(ip_addr) + '__' + str(hostname) + '__' + str(mac)
                if 'None' not in line:
                    response.append(line)
        else:
            response = ['NaN']
        return response

    def get_ipv6_by_network(self, network) -> list:
        id_net = self.get_id_net_by_network(network)
        if id_net != 0:
            cursor = self.conn.cursor(buffered=True)
            query = f"select ip_addr, hostname, mac from ipaddresses where subnetId = {id_net} and state=4;"
            cursor.execute(query)
            response: list = []
            for (ip_addr, hostname, mac) in cursor:
                ip_addr = Tools.int_to_ipv6(int(ip_addr))
                line = str(ip_addr) + '__' + str(hostname) + '__' + str(mac)
                if 'None' not in line:
                    response.append(line)
        else:
            response = ['NaN']
        return response

    def registration_test(self, mac: str, subnet_id: int) -> bool:
        '''
        testa se o mac está cadastrado no IPPAM
        :return: 1 ou 0
        '''
        cursor = self.conn.cursor(buffered=True)
        query = f"select id from ipaddresses where mac = '{mac}' and subnetId = {subnet_id} limit 1;"
        cursor.execute(query)
        for _ in cursor:
            return True
        return False

    def get_subnet_id_by_network(self, network: str):
        cursor = self.conn.cursor(buffered=True)
        query = f"select id from subnets where subnet = '{network}';"
        print(query)
        cursor.execute(query)
        response = 0
        for id in cursor:
            response = id[0]
        return response

    def get_last_edit_ip(self, subnetId: int) -> str:
        cursor = self.conn.cursor(buffered=True)
        query = f"select editDate from ipaddresses where subnetId ='{subnetId}';"
        cursor.execute(query)
        # comp é uma data anterior, como referência apenas
        try:
            comp = datetime(2021, 11, 17)
            for editDate in cursor:
                diff_date = comp - editDate[0]
                if diff_date.total_seconds() < 0.0:
                    # se a diferença entre a data atual e a data anterior é um numero negativo
                    # que dizer que a data atual é posterior, e aí atuliza como maior data
                    comp = editDate[0]
        except:
            comp = datetime(2021, 11, 17)
        return comp

    def insert_ipaddresses(self, subnetId: int, ip_addr: int, hostname: str, mac: str, is_gateway: int = 0,
                           description: str = 'NULL', state: int = 1):
        cursor = self.conn.cursor(buffered=True)
        timestamp = datetime.timestamp(datetime.now())
        dt_object = datetime.fromtimestamp(timestamp)
        editDate = str(dt_object).split('.')[0]
        try:
            sql = f"INSERT INTO ipaddresses(subnetId, ip_addr, hostname, mac, is_gateway, description, state, editDate)  " \
                  f"VALUE({subnetId}, '{ip_addr}', '{hostname}', '{mac}', {is_gateway}, '{description}', {state}, '{editDate}');"
            print(sql)
            cursor.execute(sql)
        except:
            pass

        self.conn.commit()

    def update_ipaddresses(self, subnetId: int, ip_addr: str, mac: str, is_gateway: int = 0,
                           description: str = 'NULL', hostname: str = 'NULL', state: int = 4):
        cursor = self.conn.cursor(buffered=True)

        sql = f"UPDATE ipaddresses SET mac='{mac}', " \
              f"is_gateway={is_gateway},description='{description}', state = {state} " \
              f"WHERE ip_addr='{ip_addr}' AND subnetId = {subnetId};"

        if hostname != 'NULL':
            sql = f"UPDATE ipaddresses SET hostname ='{hostname}', mac='{mac}', " \
                  f"is_gateway={is_gateway},description='{description}', state = {state} " \
                  f"WHERE ip_addr='{ip_addr}' AND subnetId = {subnetId};"
        print(sql)
        cursor.execute(sql)
        self.conn.commit()

    def get_network_id_by_ip(self, ip: str) -> int:
        ip = Tools.convert_ip_to_int(ip)
        network_id: int = 0
        cursor = self.conn.cursor(buffered=True)
        query = f"select subnetId from ipaddresses where ip_addr = '{ip}';"
        cursor.execute(query)
        for id in cursor:
            network_id = id[0]
        return network_id

    def get_network_id_by_ipv6(self, ip: str) -> int:
        ip = Tools.convert_ipv6_to_int(ip)
        network_id: int = 0
        cursor = self.conn.cursor(buffered=True)
        query = f"select subnetId from ipaddresses where ip_addr = '{ip}';"
        cursor.execute(query)
        for id in cursor:
            network_id = id[0]
        return network_id

    # para garantir que não há dhcp vazio
    def no_dhcp_null(self):
        cursor = self.conn.cursor(buffered=True)
        mac_random = Tools.random_number()
        sql = f"UPDATE ipaddresses SET mac='{mac_random}' where mac IS NULL OR mac = '';"
        cursor.execute(sql)
        self.conn.commit()


if __name__ == '__main__':
    db = Dbphpipam()
    # networks = db.get_id_net_by_ip('192.168.2.11')  # 3232263702
    # print(networks)
    print(db.get_ip_by_network('192.168.76.0'))
