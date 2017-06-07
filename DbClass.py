class DbClass:
    def __init__(self):
        import mysql.connector as connector

        self.__dsn = {
            "host": "localhost",
            "user": "caitlin",
            "passwd": "some_pass",
            "db": "ENMDatabase"
        }

        self.__connection = connector.connect(**self.__dsn)
        self.__cursor = self.__connection.cursor()

    def getDataFromDatabase(self):
        # Query zonder parameters
        sqlQuery = "SELECT * FROM Metingen"
        self.__cursor.execute(sqlQuery)
        result = self.__cursor.fetchall()
        self.__cursor.close()
        return result

    def getDataFromDatabaseMetVoorwaarde(self, voorwaarde, voorwaarde2):
        # Query met parameters
        sqlQuery = "SELECT * FROM Gebruikers WHERE Emailadres = '{param1}' and Wachtwoord_hash = MD5('{param2}')"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(param1=voorwaarde, param2=voorwaarde2)
        
        self.__cursor.execute(sqlCommand)
        result = self.__cursor.fetchall()
        # self.__cursor.close()
        return result

    def setDataToDatabaseGebruikers(self, value1, value2, value3):
        # Query met parameters
        sqlQuery = "INSERT INTO Gebruikers(Naam, Emailadres, Wachtwoord_hash) VALUES ('{param1}', '{param2}', md5('{param3}'))"
        # Combineren van de query en parameter
        sqlCommand = sqlQuery.format(param1=value1, param2=value2, param3=value3)

        self.__cursor.execute(sqlCommand)
        self.__connection.commit()
        self.__cursor.close()