import os
import csv
import database.ConnectionDb
initdb = database.ConnectionDb.run
import pandas as pd
datas = initdb.fetchData()

# Pastikan direktori 'storage/' ada
os.makedirs("storage", exist_ok=True)

# Tentukan path file tujuan
file_path = os.path.join("utils", "sinkronasi.csv")


# Transformasi data: ganti key 'claster' jadi 'kecamatan', dan tambahkan 'claster'
modified_datas = []
for row in datas:
    new_row = row.copy()
    new_row['kecamatan'] = new_row.pop('claster')  # ganti nama kolom
    new_row['claster'] = row['claster']            # tambahkan kolom claster kembali
    modified_datas.append(new_row)

with open(file_path, mode="w", newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=modified_datas[0].keys())
    writer.writeheader()
    writer.writerows(modified_datas)
