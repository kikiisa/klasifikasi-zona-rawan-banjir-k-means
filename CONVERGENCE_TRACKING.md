# Convergence Tracking in K-Means - Documentation

## Overview
Fitur konvergensi telah ditambahkan ke K-Means clustering untuk melacak dan menampilkan seberapa baik model menyatu selama proses iterasi.

## Apa itu Convergence?

**Konvergensi** adalah keadaan di mana algoritma K-Means telah mencapai stabilitas, di mana perubahan centroid sangat kecil atau tidak ada perubahan sama sekali.

**Inertia** adalah metrik yang mengukur jarak total dalam cluster (Within-Cluster Sum of Squares):
```
Inertia = Σ ||x_i - c_k||²  untuk semua x_i dalam cluster k
```

Semakin rendah inertia, semakin baik clusteringnya.

## Features Added

### 1. **Inertia Tracking per Iterasi**
- Setiap iterasi K-Means sekarang menghitung dan melacak inertia
- Stored dalam `log_iterasi[i]['inertia']`

### 2. **Convergence Change Percentage**
- Perubahan inertia dari iterasi sebelumnya dihitung sebagai persentase
- Formula: `(|inertia_current - inertia_prev| / inertia_prev) * 100`
- Stored dalam `log_iterasi[i]['convergence_change']`

### 3. **Convergence Plot Visualization**
- Grafik menampilkan inertia vs iterasi
- Membantu visualisasi proses konvergensi
- Path: `static/convergence_plot.png`
- Label nilai ditampilkan pada setiap titik

### 4. **Convergence Statistics Table**
- Tabel ringkas menampilkan:
  - Nomor iterasi
  - Nilai inertia
  - Persentase perubahan konvergensi per iterasi

## Implementation Details

### Files Modified

#### `services/ml_service.py`

**Method `run_kmeans_steps()`:**
```python
def run_kmeans_steps(self, data_scaled_df):
    # Returns: (log_iterasi, centroids, inertia_history)
    # NEW: Tracks inertia and convergence_change in each iteration log
    # NEW: Returns inertia_history list
```

**New Method `plot_convergence()`:**
```python
def plot_convergence(self, inertia_history):
    # Creates convergence curve visualization
    # X-axis: Iteration number
    # Y-axis: Inertia (WCSS)
    # Returns path to saved plot image
```

**Method `process()`:**
```python
def process(self, input_file):
    # Now returns additional keys:
    # - 'inertia_history': List of inertia values per iteration
    # - 'convergence_plot': Path to convergence plot image
    # - 'centroid_plot': Path to centroid plot image
```

**Function `process_clustering()`:**
```python
def process_clustering():
    # Now passes to template:
    # - convergence_plot: Image path
    # - convergence_table: HTML table with convergence stats
    # - inertia_history: Raw inertia values
    # - centroid_plot: Image path
```

#### `templates/klaster/hasil.html`

**New Sections Added:**
1. **Convergence Curve & Clustering Result** (Side by side)
   - Plot di card sebelah kiri
   - Cluster visualization di sebelah kanan

2. **Convergence Statistics Table**
   - Tabel dengan 3 kolom:
     - Iterasi
     - Inertia
     - Convergence Change (%)

3. **Enhanced Iteration Logs**
   - Each iteration now displays:
     - Inertia value (badge)
     - Convergence change % (badge)

## How to Use

### 1. **Process Data**
```
1. Go to /cluster-data (Clustering Management)
2. Click "Sinkronasi Data" (Synchronize)
3. Click "Prosessing Cluster" to start clustering
```

### 2. **View Convergence Results**
After processing completes, you'll see:
- **Convergence Curve** - Shows inertia trend
- **Convergence Table** - Detailed stats per iteration
- **Iteration Details** - Each iteration shows inertia & convergence %

### 3. **Interpret Results**
```
✓ Inertia decreasing = Good convergence
✓ Convergence change < 1% = Model nearly converged
✓ Flat line in plot = Model has fully converged
```

## Data Structure

### log_iterasi Entry
Each iteration log now contains:
```python
{
    'iterasi': 1,                              # Iteration number
    'rumus': 'Jarak Euclidean: √Σ(x_i - c_i)²',
    'jarak_html': '<table>...</table>',        # Distance matrix
    'assign_html': '<table>...</table>',       # Cluster assignments
    'centroid_html': '<table>...</table>',     # New centroids
    'inertia': 245.3819,                       # NEW: Inertia value
    'convergence_change': 2.3456               # NEW: Change % (None for first iteration)
}
```

### Result Dictionary
```python
result = {
    'data_scaled': DataFrame,                  # Scaled data
    'centers': DataFrame,                      # Cluster centers
    'result': DataFrame,                       # Final clusters
    'log_iterasi': List,                       # Iteration logs with convergence
    'kmeans': KMeans,                          # sklearn model
    'inertia_history': [245.3, 240.1, ...],   # NEW: Inertia values per iteration
    'centroid_plot': 'static/centroid_plot.png',
    'convergence_plot': 'static/convergence_plot.png'  # NEW
}
```

## Interpretation Examples

### Example 1: Good Convergence
```
Iterasi 1: Inertia = 245.38, Convergence Change = N/A
Iterasi 2: Inertia = 240.12, Convergence Change = 2.14%
Iterasi 3: Inertia = 238.95, Convergence Change = 0.49%
Iterasi 4: Inertia = 238.91, Convergence Change = 0.02% ← Nearly converged
```
✓ Smooth decrease → Good convergence

### Example 2: Early Convergence
```
Iterasi 1: Inertia = 245.38, Convergence Change = N/A
Iterasi 2: Inertia = 238.94, Convergence Change = 2.61%
Iterasi 3: [Converged - No more iterations]
```
✓ Fast convergence → Efficient clustering

## API Reference

### KMeansProcessor Methods

```python
processor = KMeansProcessor(n_clusters=3, random_state=42)

# Returns: (log_iterasi, centroids, inertia_history)
log_iterasi, centroids, inertia_history = processor.run_kmeans_steps(data_scaled_df)

# Visualize convergence
convergence_plot_path = processor.plot_convergence(inertia_history)
# Returns: 'static/convergence_plot.png'

# Complete pipeline with convergence tracking
result = processor.process('storage/sinkronasi.csv')
# result['convergence_plot'] = path to plot
# result['inertia_history'] = list of inertia values
```

## UI Elements Added

### Badges
- **Inertia Badge**: Shows inertia value per iteration
  - Class: `badge badge-info`
  
- **Convergence Change Badge**: Shows change percentage
  - Class: `badge badge-success`

### Images
- **Convergence Plot**: Line graph with markers
  - Located: `static/convergence_plot.png`
  - Shows trend of inertia over iterations
  
- **Centroid Plot**: Scatter plot with cluster points
  - Located: `static/centroid_plot.png`
  - Shows final clustering result

## Performance Notes

- Convergence tracking adds minimal overhead
- Plot generation takes ~0.5-1 second
- Images saved as PNG (100 DPI)
- Cache busting: Random query param added to image URLs

## Troubleshooting

### Convergence plot not showing?
1. Check if `static/` folder exists
2. Check file permissions
3. Reload page with Ctrl+Shift+R (browser cache clear)

### Inertia values seem wrong?
1. Ensure data is properly scaled (MinMaxScaler)
2. Check feature columns: ['curah_hujan', 'kemiringan', 'banjir_histori']
3. Verify data types are numeric

### Plot quality issues?
1. Increase DPI in `plot_convergence()`: change `dpi=100` to `dpi=150`
2. Increase figure size: `figsize=(12, 7)` instead of `(10, 6)`

## Future Enhancements

Possible improvements:
- [ ] Interactive convergence plot (Chart.js/Plotly)
- [ ] Export convergence data to CSV
- [ ] Convergence threshold customization
- [ ] Silhouette score visualization
- [ ] Elbow method plot for optimal k
- [ ] Real-time convergence monitoring

## Related Files

- Main Service: `services/ml_service.py`
- Template: `templates/klaster/hasil.html`
- Test Script: `test_ml_fix.py`
- Config: `index.py` routes

---

**Status**: ✅ Actively Used  
**Version**: 1.0  
**Last Updated**: 2024
