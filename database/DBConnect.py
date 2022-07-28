import mysql.connector
from mysql.connector import errorcode
from config import conf as data


class Connect:

    def conn(self):
        db_connection = ''
        config = {
            'user': data.db_user,
            'password': data.db_pass,
            'host': data.db_host,
            'database': data.db_name,
        }
        try:
            db_connection = mysql.connector.connect(**config)
            #print("DB conectado")
            return db_connection
        except mysql.connector.Error as error:
            if error.errno == errorcode.ER_BAD_DB_ERROR:
                print("DB não existe")
            elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Usuário ou senha inválido")
            else:
                print(error)
        else:
            db_connection.close()

        return db_connection
