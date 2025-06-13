import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)

# Generate 100 rows of random data
num_samples = 100

# ID from 1 to 100
ids = list(range(1, num_samples + 1))

# Latitude and Longitude within a reasonable range near the example
latitudes = np.random.uniform(-0.8500, -0.8300, num_samples)
longitudes = np.random.uniform(123.0400, 123.0800, num_samples)

# Elevation between 30 and 120 meters
elevations = np.random.randint(30, 121, num_samples)

# Curah Hujan between 2400 and 3200 mm/year
curah_hujan = np.random.randint(2400, 3201, num_samples)

# Jarak ke Sungai between 10 and 300 meters
jarak_sungai = np.random.randint(10, 301, num_samples)

# Kemiringan between 0 and 15%
kemiringan = np.random.randint(0, 16, num_samples)

# Penggunaan Lahan choices
lahan_choices = ['Permukiman', 'Sawah', 'Hutan', 'Perkebunan']
penggunaan_lahan = [random.choice(lahan_choices) for _ in range(num_samples)]

# Riwayat Banjir between 0 and 5 times
riwayat_banjir = np.random.randint(0, 6, num_samples)

# Create DataFrame
df = pd.DataFrame({
    'id': ids,
    'latitude': latitudes,
    'longitude': longitudes,
    'elevation_m': elevations,
    'curah_hujan_mm': curah_hujan,
    'jarak_sungai_m': jarak_sungai,
    'kemiringan_persen': kemiringan,
    'landuse': penggunaan_lahan,
    'banjir_historis': riwayat_banjir
})

# Save DataFrame to CSV
df.to_csv('dataset/dataset.csv', index=False)
