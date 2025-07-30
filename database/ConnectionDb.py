import mysql.connector
from mysql.connector import Error
import pandas as pd
from werkzeug.security import generate_password_hash



class ConnectionDb:  # Fixed typo: Claster -> Cluster
    def __init__(self):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": "",  # Empty password
            "database": "development_banjir",
            "port": 3306,   
            "charset": "utf8mb4",
            "autocommit": False
        }
        self.db = None
        self.connect_to_database()
    def query_db(self):
        return self.db

    def connect_to_database(self):
        try:
            self.db = mysql.connector.connect(**self.config)
            if self.db.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print("Error while connecting to MySQL database")
    def create_table_cluster(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE claster (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lng TEXT NOT NULL,
                lat TEXT NOT NULL,
                nama_desa TEXT NOT NULL,
                curah_hujan TEXT NOT NULL,
                kemiringan TEXT NOT NULL,
                banjir_histori TEXT NOT NULL,
                geojson VARCHAR(255),
                claster VARCHAR(255)
            )
        """)
        print("Table 'claster' created successfully")
        self.db.commit()
        cursor.close()
        
    def createTableUer(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                status ENUM('active','inactive'),
                role ENUM('admin','operator') NOT NULL
            )
        """)
        self.db.commit()
        cursor.close()
        print("Table 'users' created successfully")
        
    def insert_data_cluster(self):
        cursor = self.db.cursor()
        df = pd.read_csv("dataset/result.csv")
        df = df.rename(columns={
            'longitude': 'lng',
            'latitude': 'lat',
            'desa': 'nama_desa',
            'curah_hujan_mm': 'curah_hujan',
            'kemiringan_persen': 'kemiringan',
            'banjir_historis': 'banjir_histori'
        })        
        insert_query = """
            INSERT INTO claster (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        for index, row in df.iterrows():
            cursor.execute(insert_query, (row['lng'], row['lat'], row['nama_desa'], row['curah_hujan'], row['kemiringan'], row['banjir_histori']))
        self.db.commit()
        cursor.close()
        print("Data inserted successfully")
    
    def fetchData(self):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM claster")
        data = cursor.fetchall()
        cursor.close()
        return data

    def getUserByUsername(self, username):
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        return user    
    
    def getVillaeByDistrict(self,id):
        cursor = self.db.cursor(dictionary=True)
        query = "SELECT * FROM claster WHERE claster = %s"
        cursor.execute(query, (id,))
        village = cursor.fetchall()
        cursor.close()
        return village
    
    
    def updateUser(self, user_id, username, full_name, email, password, status, role):
        cursor = self.db.cursor()
        if password:  # Jika password tidak kosong, update password juga
            hashed_password = generate_password_hash(password)
            update_query = """
                UPDATE users
                SET username = %s,
                    full_name = %s,
                    email = %s,
                    password = %s,
                    status = %s,
                    role = %s
                WHERE id = %s
            """
            values = (username, full_name, email, hashed_password, status, role, user_id)
        else:  # Jika password kosong, abaikan kolom password
            update_query = """
                UPDATE users
                SET username = %s,
                    full_name = %s,
                    email = %s,
                    status = %s,
                    role = %s
                WHERE id = %s
            """
            values = (username, full_name, email, status, role, user_id)
        cursor.execute(update_query, values)
        self.db.commit()
        cursor.close()
    
    def insertData(self, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson,kecamatan):
        cursor = self.db.cursor()
        insert_query = "INSERT INTO claster (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson,claster) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson,kecamatan))
        self.db.commit()
        cursor.close()
        
    def insertUser(self, username, full_name, email, password, status, role):
        cursor = self.db.cursor()
        insert_query = """
            INSERT INTO users (username, full_name, email, password, status, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        hashed_password = generate_password_hash(password)
        cursor.execute(insert_query, (username, full_name, email,hashed_password, status, role))
        self.db.commit()
        cursor.close()
        
    
    def editUser(self,id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        data = cursor.fetchone()
        cursor.close()
        return data
    
    
    def fetchDataUserById(self, id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM claster WHERE id = %s", (id,))
        data = cursor.fetchone()
        cursor.close()
        return data
    
    def fetchDataUser(self):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        cursor.close()
        return data
    
    def deleteData(self, id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM claster WHERE id = %s", (id,))
        self.db.commit()
        cursor.close()
        
    def updateData(self, id, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson,kecamatan):
        cursor = self.db.cursor()
        update_query = "UPDATE claster SET lng = %s, lat = %s, nama_desa = %s, curah_hujan = %s, kemiringan = %s, banjir_histori = %s, geojson = %s, claster = %s WHERE id = %s"
        cursor.execute(update_query, (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson,kecamatan, id))
        self.db.commit()
        cursor.close()
        
    def updateDataNoData(self, id, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori,kecamatan):
        cursor = self.db.cursor()
        update_query = "UPDATE claster SET lng = %s, lat = %s, nama_desa = %s, curah_hujan = %s, kemiringan = %s, banjir_histori = %s, claster = %s WHERE id = %s"
        cursor.execute(update_query, (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori,kecamatan, id))
        self.db.commit()
        cursor.close()
        
    def deleteUser(self,id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        self.db.commit()
        cursor.close()
    
        
run = ConnectionDb()
# run.create_table_cluster()
# run.createTableUer()
# run.insert_data_cluster()

