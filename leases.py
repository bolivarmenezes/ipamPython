import socket
from config import conf as data
import re
from database.DBphpipam import Dbphpipam
from database.DBparser import DBparser
from tools import Tools


class ManagerLeases:

    def __init__(self):
        self.path_leases = data.dhcp_leases
        self.insert_addresses_by_leases()

    def get_ip_mac(self):
        '''
        Filtra das leases os endereços, resolve os nomes e ignora os que não resolverem
        :return: lista contendo -> MAC__IP__NAME
        '''
        pattern = re.compile(r"lease ([0-9.]+) {.*?hardware ethernet ([:a-f0-9]+);.*?}", re.MULTILINE | re.DOTALL)
        response: list = []
        with open(self.path_leases) as f:
            for match in pattern.finditer(f.read()):
                try:
                    ip = str(match.group(1))
                    if '172.21' not in ip:
                        name = Tools.getNameByIP(ip)
                        if 'eduroam' not in name:
                            mac = str(match.group(2))
                            try:
                                response.append(f"{mac}__{ip}__{name}")
                            except socket.herror:
                                pass
                                # print(f"IP não resolveu: {ip}")
                            except IndexError:
                                pass
                            except KeyboardInterrupt:
                                print("Cancelado")
                except:
                    pass
        return response

    def insert_addresses_by_leases(self) -> bool:
        db = Dbphpipam()
        # testa se o mac está cadastrado no IPPAM
        address = self.get_ip_mac()
        db_parser = DBparser()

        for addr in address:
            mac = str(addr).split('__')[0]
            ip = str(addr).split('__')[1]

            hostname = str(addr).split('__')[2]
            subnetId = db.get_network_id_by_ip(ip)
            test = db.registration_test(mac, subnetId)

            if test is False and subnetId != 0:
                # pega a rede pelo IP
                print(f"ID Rede:{subnetId} MAC: {mac} Nome:{hostname} IP: {ip} ainda não cadastrado")
                # cadastra no mysql do phpipam
                ip = Tools.convert_ip_to_int(ip)
                db.update_ipaddresses(subnetId, ip, hostname, mac, 0, 'add by arpwatch', 4)

        response = False

        return response


if '__main__' == __name__:
    ml = ManagerLeases()

