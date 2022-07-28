import socket
from config import conf as data
import re
from database.DBphpipam import Dbphpipam
from database.DBparser import DBparser
from tools import Tools


class ManagerArpWatch:

    def __init__(self):
        self.path_file = data.arp_watch
        self.insert_addresses_by_arpwatch()

    def get_ip_mac(self):
        '''
        Filtra do arpwatch os endereços, resolve os nomes e ignora os que não resolverem
        :return: lista contendo -> MAC__IP__NAME
        '''
        with open(self.path_file) as file:
            lines = file.readlines()
        response: list = []
        for line in lines:
            try:
                mac = re.search(r'([0-9A-F]{1,2}[:-]){5}([0-9A-F]{1,2})', line, re.I)[0]
                mac = Tools.format_mac(str(mac))
                ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line, re.I)[0]
                try:
                    name = Tools.getNameByIP(ip)
                    response.append(f"{mac}__{ip}__{name}")
                except socket.herror:
                    print(f"IP não resolveu: {ip}")
            except IndexError:
                pass
        return response

    def insert_addresses_by_arpwatch(self) -> bool:
        '''
        testa se o mac está cadastrado no IPPAM, se não está, cadastra
        :return: 1 ou 0
        ANTES DE FAZER TUDO ISSO, É NECESSÁRIO FAZER O CADASTRO PRÉVIO DE TODOS OS IPs QUE SERÃO UTILIZADOS NO DHCP,NO PHPIPAM
        '''
        db = Dbphpipam()
        # testa se o mac está cadastrado no IPPAM
        address = self.get_ip_mac()
        db_parser = DBparser()

        for addr in address:
            mac = str(addr).split('__')[0]
            ip = str(addr).split('__')[1]

            # pega o hostname atual, apenas para adicionar no description
            description = str(addr).split('__')[2]
            subnetId = db.get_network_id_by_ip(ip)
            test = db.registration_test(mac, subnetId)

            if test is False and subnetId != 0:
                # pega a rede pelo IP
                print(f"ID Rede:{subnetId} MAC: {mac} Nome:{description} IP: {ip} ainda não cadastrado")
                # cadastra no mysql do phpipam
                ip = Tools.convert_ip_to_int(ip)
                db.update_ipaddresses(subnetId, ip, mac, is_gateway=0, description=description, state=4)

        response = False

        return response


if '__main__' == __name__:
    ManagerArpWatch()
