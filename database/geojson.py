import json
from shapely.geometry import Point, shape
import ConnectionDb

db = ConnectionDb.run


# 1. Baca file geojson
with open("data.geojson", "r") as f:
    geojson_data = json.load(f)


data_lokasi = db.fetchData()

# 3. Cek untuk setiap titik, apakah berada dalam salah satu feature
for data in data_lokasi:
    point = Point(data["lng"], data["lat"])
    ditemukan = False

    for feature in geojson_data["features"]:
        geometry = shape(feature["geometry"])  # MultiPolygon

        if geometry.contains(point):
            print(f"{data['nama_desa']} berada di dalam")
            ditemukan = True
            break  # Stop setelah ketemu

    if not ditemukan:
        print(f"{data['nama_desa']} TIDAK berada dalam area manapun.")

