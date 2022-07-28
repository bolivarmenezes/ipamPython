import socket
import struct
import random
from binascii import hexlify
import ipaddress


class Tools:

    @staticmethod
    def format_mac(mac: str) -> str:
        new_mac = mac.lower()
        if ':' not in new_mac:
            new_mac = new_mac.replace(' ', ':')
        else:
            new_mac = new_mac.strip()

        # testa se o MAC está com tamanho ok
        if len(new_mac) == 17:
            return new_mac
        # se for diferente de 17, quebra o MAC em 6 octetos
        elif len(new_mac) < 17:
            mac_sliced = new_mac.split(":")
            new_line = ''
            for line in mac_sliced:
                if len(line) == 2:
                    new_line = new_line + line + ':'
                else:
                    new_line += '0' + line + ':'

            # remove, se houver, os dois pontos nos final do arquivo
            if new_line[-1] == ':':
                new_line = new_line[:-1]
                return new_line
            return new_mac

    @staticmethod
    def getNameByIP(ip:str):
        name = socket.gethostbyaddr(ip)[0]
        if '.ufsm.br.' in name and 'in-addr' not in name:
            name = name.split('.ufsm.br.')[0]
        elif 'in-addr' in name:
            name = name.split('.ufsm.br.')[0]+'.ufsm.br'


        return name

    @staticmethod
    def convert_ip_to_int(ip: str) -> str:
        return struct.unpack("!I", socket.inet_aton(ip))[0]

    def convert_ipv6_to_int(ipv6_addr: str) -> int:
        return int(hexlify(socket.inet_pton(socket.AF_INET6, ipv6_addr)),16)

    @staticmethod
    def random_number():
        return str(random.randint(1000000,10000000000))

    @staticmethod
    def int_to_ipv6(ip_int:int):
        response = ipaddress.IPv6Address(ip_int)
        return response


if '__main__' == __name__:
    #print(Tools.getNameByIP('192.168.76.227'))
    pass