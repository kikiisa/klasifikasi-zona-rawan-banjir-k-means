import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import requests


class KMeansController:
    def __init__(self):
        pass
    
    def getDataFromCSV(self):
        data = pd.read_csv('dataset/dataset.csv')
        return data

    
    def getCombinedData(self):
        data_csv = self.getDataFromCSV()
        
    
        # Pastikan kolom sama
        if not data_api:
            missing_cols = set(data_csv.columns) - set(data_api.columns)
            print(missing_cols)
            for col in missing_cols:
                data_api[col] = None  # Tambahkan kolom kosong jika tidak ada

            # Urutkan kolom agar sesuai
            data_api = data_api[data_csv.columns]

        # # Gabungkan data
        # combined = pd.concat([data_csv, data_api], ignore_index=True)
        # return combined
    
initial = KMeansController()
