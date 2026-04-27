"""Machine Learning Service - K-means clustering and data processing"""
import os
import pandas as pd
import numpy as np
import csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from flask import flash, render_template, redirect, url_for
import database.ConnectionDb
from .utils import login_required
from .data_validation import validate_dataframe_features

initDb = database.ConnectionDb.run
DATASET_DIR = 'storage'
THRESHOLD_COLUMNS = [
    'interpretasi_curah_hujan',
    'interpretasi_kemiringan',
    'interpretasi_banjir_histori',
    'interpretasi_threshold'
]


def _to_number(value):
    """Convert raw value to float when possible."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_curah_hujan(value):
    """Classify rainfall threshold."""
    value = _to_number(value)
    if value is None:
        return 'tidak diketahui'
    if value < 2600:
        return 'rendah'
    if value < 2800:
        return 'sedang'
    return 'tinggi'


def classify_kemiringan(value):
    """Classify slope threshold."""
    value = _to_number(value)
    if value is None:
        return 'tidak diketahui'
    if value < 5:
        return 'landai'
    if value < 8:
        return 'sedang'
    return 'curam'


def classify_banjir_histori(value):
    """Classify flood-history threshold."""
    value = _to_number(value)
    if value is None:
        return 'tidak diketahui'
    if value == 0:
        return 'tidak pernah'
    if value < 3:
        return 'pernah'
    return 'sering'


def build_threshold_interpretation(row):
    """Build derived threshold interpretations for a dataset row."""
    curah_hujan = classify_curah_hujan(row.get('curah_hujan'))
    kemiringan = classify_kemiringan(row.get('kemiringan'))
    banjir_histori = classify_banjir_histori(row.get('banjir_histori'))

    return {
        'interpretasi_curah_hujan': curah_hujan,
        'interpretasi_kemiringan': kemiringan,
        'interpretasi_banjir_histori': banjir_histori,
        'interpretasi_threshold': (
            f"Curah hujan {curah_hujan}, "
            f"kemiringan {kemiringan}, "
            f"histori banjir {banjir_histori}"
        )
    }


def enrich_threshold_columns(data):
    """Ensure threshold interpretation columns are available and up to date."""
    threshold_df = data.apply(build_threshold_interpretation, axis=1, result_type='expand')
    for column in THRESHOLD_COLUMNS:
        data[column] = threshold_df[column]
    return data


class KMeansProcessor:
    """K-means clustering processor"""
    
    def __init__(self, n_clusters=3, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = MinMaxScaler()
        self.features = ['curah_hujan', 'kemiringan', 'banjir_histori']
        
    def load_data(self, file_path):
        """Load data from CSV file"""
        data = pd.read_csv(file_path)
        return enrich_threshold_columns(data)
    
    def preprocess_data(self, data):
        """Preprocess and scale data"""
        validated_data = validate_dataframe_features(data, context_label='data K-Means')
        data_scaled = self.scaler.fit_transform(validated_data[self.features])
        return validated_data, pd.DataFrame(data_scaled, columns=self.features)
    
    def run_kmeans_steps(self, data_scaled_df):
        """Run K-means with step-by-step logging and convergence tracking"""
        k = self.n_clusters
        np.random.seed(self.random_state)
        centroids = data_scaled_df.sample(n=k).to_numpy()

        log_iterasi = []
        inertia_history = []
        centroid_history = []
        max_iter = 10
        
        for i in range(max_iter):
            # Calculate Euclidean distance
            distances = np.sqrt(((data_scaled_df.to_numpy()[:, None] - centroids[None, :]) ** 2).sum(axis=2))
            assign = np.argmin(distances, axis=1)

            # Calculate inertia (within-cluster sum of squares) - for convergence tracking
            inertia = np.sum(np.min(distances ** 2, axis=1))
            inertia_history.append(inertia)
            centroid_history.append(centroids.copy())

            # Create log HTML tables
            jarak_df = pd.DataFrame(distances, columns=[f'C{j}' for j in range(k)])
            centroid_df = pd.DataFrame(centroids, columns=self.features)

            # Calculate convergence change
            convergence_change = None
            if i > 0:
                prev_inertia = inertia_history[i-1]
                convergence_change = abs(prev_inertia - inertia) / prev_inertia * 100 if prev_inertia != 0 else 0

            log_iterasi.append({
                'iterasi': i + 1,
                'rumus': 'Jarak Euclidean: √Σ(x_i - c_i)²',
                'jarak_html': jarak_df.to_html(classes='table table-bordered'),
                'centroid_html': centroid_df.to_html(classes='table table-bordered'),
                'inertia': inertia,
                'convergence_change': convergence_change,
                'is_converged': False,
                'convergence_message': None
            })

            # Update new centroid
            new_centroids = np.array([
                data_scaled_df.to_numpy()[assign == j].mean(axis=0) 
                if np.any(assign == j) 
                else centroids[j]
                for j in range(k)
            ])

            if np.allclose(centroids, new_centroids):
                log_iterasi[-1]['is_converged'] = True
                log_iterasi[-1]['convergence_message'] = f'Konvergensi tercapai pada iterasi ke-{i + 1}'
                print(f"Converged at iteration {i + 1}")
                break
            
            centroids = new_centroids

        return log_iterasi, centroids, inertia_history
    
    def fit_kmeans(self, data_scaled_df):
        """Fit K-means using sklearn"""
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        kmeans.fit(data_scaled_df)
        return kmeans
    
    def map_clusters(self, data, kmeans):
        """Map cluster numbers to risk levels"""
        fitur = self.features
        mapping = {0: 'Tidak Rawan', 1: 'Rawan', 2: 'Sangat Rawan'}
        
        centers = pd.DataFrame(kmeans.cluster_centers_, columns=fitur)
        order = centers['curah_hujan'].argsort().values
        label_map = {old: mapping[new] for new, old in enumerate(order)}
        
        # Use scaler.transform() instead of fit_transform() (already fitted)
        # Use kmeans.predict() instead of fit_predict() (already fitted)
        data_scaled = pd.DataFrame(
            self.scaler.transform(data[fitur]), 
            columns=fitur
        )
        predictions = kmeans.predict(data_scaled)
        data['claster'] = pd.Series(predictions).map(label_map).values
        
        return data, centers, label_map
    
    def plot_centroid_and_clusters(self, data_scaled_df, data, kmeans, mapping):
        """Plot centroid and clusters"""
        k = self.n_clusters
        plt.figure(figsize=(10, 6))

        for cluster in range(k):
            # Get cluster label name
            label_name = mapping.get(cluster, f'Cluster {cluster}')
            cluster_data = data_scaled_df[data['claster'] == label_name]
            plt.scatter(cluster_data['curah_hujan'], cluster_data['kemiringan'], label=f'{label_name}')

        # Plot centroid
        centroids_plot = kmeans.cluster_centers_
        plt.scatter(centroids_plot[:, 0], centroids_plot[:, 1],
                    s=300, c='red', marker='X', label='Centroid', edgecolors='black', linewidth=2)

        plt.xlabel('Curah Hujan')
        plt.ylabel('Kemiringan')
        plt.legend()
        plt.title('K-Means Clustering Result')
        plt.grid(True, alpha=0.3)

        centroid_path = "static/centroid_plot.png"
        os.makedirs(os.path.dirname(centroid_path), exist_ok=True)
        plt.savefig(centroid_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return centroid_path
    
    def plot_convergence(self, inertia_history):
        """Plot convergence curve (inertia over iterations)"""
        plt.figure(figsize=(10, 6))
        
        iterations = range(1, len(inertia_history) + 1)
        plt.plot(iterations, inertia_history, 'b-o', linewidth=2, markersize=6)
        
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
        plt.title('K-Means Convergence Curve', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Add value labels on points
        for i, val in enumerate(inertia_history):
            plt.text(i + 1, val, f'{val:.2f}', ha='center', va='bottom', fontsize=9)
        
        convergence_path = "static/convergence_plot.png"
        os.makedirs(os.path.dirname(convergence_path), exist_ok=True)
        plt.savefig(convergence_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return convergence_path
    
    def process(self, input_file):
        """Complete processing pipeline"""
        # Load data
        data = self.load_data(input_file)
        
        # Preprocess
        validated_data, data_scaled_df = self.preprocess_data(data)
        
        # Save scaled data
        data_scaled_df.to_csv(os.path.join(DATASET_DIR, "prosessing.csv"), index=False)
        
        # Run K-means with step logging (now returns inertia_history)
        log_iterasi, _, inertia_history = self.run_kmeans_steps(data_scaled_df)
        
        # Fit final K-means
        kmeans = self.fit_kmeans(data_scaled_df)
        
        # Map clusters to risk levels
        validated_data, centers, label_map = self.map_clusters(validated_data, kmeans)
        
        # Save result
        validated_data.to_csv(os.path.join(DATASET_DIR, "result.csv"), index=False)
        
        # Plot visualizations
        centroid_plot_path = self.plot_centroid_and_clusters(data_scaled_df, validated_data, kmeans, label_map)
        convergence_plot_path = self.plot_convergence(inertia_history)
        
        return {
            'data_scaled': data_scaled_df,
            'centers': centers,
            'result': validated_data,
            'log_iterasi': log_iterasi,
            'kmeans': kmeans,
            'inertia_history': inertia_history,
            'centroid_plot': centroid_plot_path,
            'convergence_plot': convergence_plot_path
        }


# Service functions

@login_required
def management_cluster_view():
    """Display clustering management page"""
    result_path = os.path.join(DATASET_DIR, 'sinkronasi.csv')
    result_path_processing = os.path.join(DATASET_DIR, 'prosessing.csv')
    result_path_final = os.path.join(DATASET_DIR, 'result.csv')

    converHTMLresultSinkronasi = None
    convertHTMLresultProcessing = None
    converHTMLresultFinal = None
    
    status_sinkronasi = os.path.isfile(result_path)
    processingData = os.path.isfile(result_path_processing)
    status_final_result = os.path.isfile(result_path_final)
    
    if status_sinkronasi:
        resultSinkronasi = pd.read_csv(result_path).drop(columns=['id', 'geojson'], errors='ignore')
        converHTMLresultSinkronasi = resultSinkronasi.to_html(classes='table table-bordered', index=False)  
    
    if processingData:
        resultProcessing = pd.read_csv(result_path_processing)
        convertHTMLresultProcessing = resultProcessing.to_html(classes='table table-bordered', index=False)
        
    if status_final_result:
        resultFinal = pd.read_csv(result_path_final).drop(columns=['id', 'geojson'], errors='ignore')
        converHTMLresultFinal = resultFinal.to_html(classes='table table-bordered', index=False)
        
    return render_template(
        'klaster/index.html',
        title='Clustering Management',
        resultSinkronasi=converHTMLresultSinkronasi,
        resultFinalData=converHTMLresultFinal,
        resultStepProsessing=convertHTMLresultProcessing,
        threshold_columns=THRESHOLD_COLUMNS
    )


@login_required
def sinkronasi_data():
    """Synchronize data from database to CSV"""
    datas = initDb.fetchData()

    if not datas:
        flash("Data Tidak Ditemukan", "danger")
        return redirect(url_for('management_cluster'))

    os.makedirs(DATASET_DIR, exist_ok=True)

    file_path = os.path.join(DATASET_DIR, "sinkronasi.csv")
    
    # Transform data
    modified_datas = []
    for row in datas:
        threshold_result = build_threshold_interpretation(row)
        new_row = {
            'id': row.get('id'),
            'lng': row.get('lng'),
            'lat': row.get('lat'),
            'nama_desa': row.get('nama_desa'),
            'curah_hujan': row.get('curah_hujan'),
            'interpretasi_curah_hujan': threshold_result['interpretasi_curah_hujan'],
            'kemiringan': row.get('kemiringan'),
            'interpretasi_kemiringan': threshold_result['interpretasi_kemiringan'],
            'banjir_histori': row.get('banjir_histori'),
            'interpretasi_banjir_histori': threshold_result['interpretasi_banjir_histori'],
            'interpretasi_threshold': threshold_result['interpretasi_threshold'],
            'geojson': row.get('geojson'),
            'kecamatan': row.get('claster'),
            'claster': row.get('claster')
        }
        modified_datas.append(new_row)

    with open(file_path, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=modified_datas[0].keys())
        writer.writeheader()
        writer.writerows(modified_datas)

    flash("Berhasil Menyinkronkan Data, Lakukan Prosessing Data", "success")
    return redirect(url_for('management_cluster'))


@login_required
def process_clustering():
    """Process clustering"""
    file_path = os.path.join(DATASET_DIR, 'sinkronasi.csv')
    
    if not os.path.isfile(file_path):
        flash('File CSV Tidak Ditemukan, Silahkan Sinkronasi Kembali', "danger")
        return redirect(url_for('management_cluster'))

    try:
        # Initialize processor
        processor = KMeansProcessor(n_clusters=3, random_state=42)
        
        # Process data
        result = processor.process(file_path)
        
        flash('Proses Berhasil', 'success')

        # Prepare result HTML
        result_path_final = os.path.join(DATASET_DIR, 'result.csv')
        if os.path.isfile(result_path_final):
            resultFinal = pd.read_csv(result_path_final).drop(
                columns=['id', 'geojson'], 
                errors='ignore'
            )
            converHTMLresultFinal = resultFinal.to_html(classes='table table-bordered', index=False)
        else:
            converHTMLresultFinal = None

        # Prepare convergence data for template
        convergence_table = pd.DataFrame({
            'Iterasi': [log['iterasi'] for log in result['log_iterasi']],
            'Inertia': [f"{log['inertia']:.6f}" for log in result['log_iterasi']],
            'Convergence Change (%)': [
                f"{log['convergence_change']:.4f}" if log['convergence_change'] is not None else "N/A"
                for log in result['log_iterasi']
            ]
        })
        convergence_html = convergence_table.to_html(classes='table table-bordered', index=False)
        converged_log = next((log for log in result['log_iterasi'] if log['is_converged']), None)
        if converged_log:
            convergence_summary = {
                'status': 'success',
                'title': 'Model Sudah Konvergen',
                'message': converged_log['convergence_message'],
                'iteration': converged_log['iterasi']
            }
        else:
            convergence_summary = {
                'status': 'warning',
                'title': 'Konvergensi Belum Terdeteksi',
                'message': f"Model berhenti sampai iterasi ke-{len(result['log_iterasi'])} tanpa penanda konvergensi.",
                'iteration': len(result['log_iterasi'])
            }

        return render_template('klaster/hasil.html',
            scaled=result['data_scaled'].to_html(classes='table table-bordered'),
            centers=result['centers'].to_html(classes='table table-bordered'),
            hasil=result['result'].to_html(classes='table table-bordered'),
            log_iterasi=result['log_iterasi'],
            final=converHTMLresultFinal,
            threshold_columns=THRESHOLD_COLUMNS,
            convergence_summary=convergence_summary,
            convergence_plot=result['convergence_plot'],
            convergence_table=convergence_html,
            inertia_history=result['inertia_history'],
            centroid_plot=result['centroid_plot']
        )
        
    except Exception as e:
        flash(f'Error saat processing: {str(e)}', 'danger')
        return redirect(url_for('management_cluster'))


def get_results():
    """Get clustering results as JSON"""
    file_path = os.path.join(DATASET_DIR, "result.csv")
    
    if not os.path.isfile(file_path):
        return None
    
    return pd.read_csv(file_path)


def get_filter_by_district(id):
    """Get villages filtered by district"""
    return initDb.getVillaeByDistrict(id)
