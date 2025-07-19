import mysql.connector
from mysql.connector import Error
import pandas as pd

class ConnectionDb:  # Fixed typo: Claster -> Cluster
    def __init__(self):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": "",  # Empty password
            "database": "cluster_banjir",
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
    def insert_data_cluster(self):
        cursor = self.db.cursor()
        df = pd.read_csv("output/result.csv")
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
    
    def insertData(self, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson):
        cursor = self.db.cursor()
        insert_query = "INSERT INTO claster (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson))
        self.db.commit()
        cursor.close()
        
    def fetchDataById(self, id):
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM claster WHERE id = %s", (id,))
        data = cursor.fetchone()
        cursor.close()
        return data
    
    def deleteData(self, id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM claster WHERE id = %s", (id,))
        self.db.commit()
        cursor.close()
    def updateData(self, id, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson):
        cursor = self.db.cursor()
        update_query = "UPDATE claster SET lng = %s, lat = %s, nama_desa = %s, curah_hujan = %s, kemiringan = %s, banjir_histori = %s, geojson = %s WHERE id = %s"
        cursor.execute(update_query, (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, geojson, id))
        self.db.commit()
        cursor.close()
    def updateDataNoData(self, id, lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori):
        cursor = self.db.cursor()
        update_query = "UPDATE claster SET lng = %s, lat = %s, nama_desa = %s, curah_hujan = %s, kemiringan = %s, banjir_histori = %s WHERE id = %s"
        cursor.execute(update_query, (lng, lat, nama_desa, curah_hujan, kemiringan, banjir_histori, id))
        self.db.commit()
        cursor.close()
run = ConnectionDb()
# run.create_table_cluster()
# run.insert_data_cluster()

