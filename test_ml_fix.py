"""
Test script untuk validate ML Service fixes
Jalankan: python test_ml_fix.py
"""
import sys
import os
sys.path.insert(0, '/home/kikiisa/Documents/web/k-means-banjir')

import pandas as pd
import numpy as np
from services.ml_service import KMeansProcessor

def test_ml_processor():
    """Test KMeansProcessor dengan dummy data"""
    print("=" * 60)
    print("Testing KMeansProcessor Fixes")
    print("=" * 60)
    
    # Create dummy data untuk test
    np.random.seed(42)
    n_samples = 50
    
    dummy_data = {
        'id': range(1, n_samples + 1),
        'nama_desa': [f'Desa{i}' for i in range(1, n_samples + 1)],
        'lng': np.random.uniform(-180, 180, n_samples),
        'lat': np.random.uniform(-90, 90, n_samples),
        'curah_hujan': np.random.uniform(100, 500, n_samples),
        'kemiringan': np.random.uniform(0, 45, n_samples),
        'banjir_histori': np.random.randint(0, 10, n_samples),
        'geojson': [''] * n_samples
    }
    
    df = pd.DataFrame(dummy_data)
    test_file = '/tmp/test_sinkronasi.csv'
    df.to_csv(test_file, index=False)
    
    print("\n✓ Created dummy dataset with {} records".format(len(df)))
    print("  Features: curah_hujan, kemiringan, banjir_histori")
    
    # Initialize processor
    print("\n✓ Initializing KMeansProcessor...")
    processor = KMeansProcessor(n_clusters=3, random_state=42)
    
    # Test 1: Load data
    print("\n[TEST 1] Loading data...")
    try:
        data = processor.load_data(test_file)
        print("  ✓ Data loaded successfully: {} rows".format(len(data)))
    except Exception as e:
        print("  ✗ ERROR: {}".format(e))
        return False
    
    # Test 2: Preprocess data
    print("\n[TEST 2] Preprocessing data...")
    try:
        validated_data, data_scaled = processor.preprocess_data(data)
        print("  ✓ Data validated successfully")
        print("  ✓ Data scaled successfully")
        print("  ✓ Scaled data shape: {}".format(data_scaled.shape))
        print("  ✓ Sample scaled values:\n{}".format(data_scaled.head()))
    except Exception as e:
        print("  ✗ ERROR: {}".format(e))
        return False
    
    # Test 3: Run K-means steps
    print("\n[TEST 3] Running K-means with step logging...")
    try:
        log_iterasi, centroids, inertia_history = processor.run_kmeans_steps(data_scaled)
        print("  ✓ K-means steps completed")
        print("  ✓ Iterations logged: {}".format(len(log_iterasi)))
        print("  ✓ Inertia history length: {}".format(len(inertia_history)))
        for i, log in enumerate(log_iterasi):
            print("    - Iterasi {}: {} (formula: {})".format(
                log['iterasi'], 
                'HTML generated' if log['jarak_html'] else 'empty',
                log['rumus'][:40] + '...'
            ))
    except Exception as e:
        print("  ✗ ERROR: {}".format(e))
        return False
    
    # Test 4: Fit K-means
    print("\n[TEST 4] Fitting K-means model...")
    try:
        kmeans = processor.fit_kmeans(data_scaled)
        print("  ✓ K-means fitted successfully")
        print("  ✓ N clusters: {}".format(kmeans.n_clusters))
        print("  ✓ Inertia: {:.4f}".format(kmeans.inertia_))
    except Exception as e:
        print("  ✗ ERROR: {}".format(e))
        return False
    
    # Test 5: Map clusters (THIS WAS THE BUG)
    print("\n[TEST 5] Mapping clusters to risk levels (FIXED)...")
    try:
        data_with_clusters, centers, label_map = processor.map_clusters(validated_data, kmeans)
        print("  ✓ Clusters mapped successfully")
        print("  ✓ Label map: {}".format(label_map))
        print("  ✓ Cluster distribution:")
        for cluster in data_with_clusters['claster'].unique():
            count = (data_with_clusters['claster'] == cluster).sum()
            print("    - {}: {} samples".format(cluster, count))
        print("  ✓ Centers DataFrame:")
        print("{}".format(centers))
    except Exception as e:
        print("  ✗ ERROR (THIS IS THE BUG): {}".format(e))
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Complete pipeline
    print("\n[TEST 6] Complete processing pipeline...")
    try:
        result = processor.process(test_file)
        print("  ✓ Complete pipeline executed successfully")
        print("  ✓ Result keys: {}".format(list(result.keys())))
        print("  ✓ Final result (first 5 rows):")
        print(result['result'][['nama_desa', 'curah_hujan', 'kemiringan', 'claster']].head())
    except Exception as e:
        print("  ✗ ERROR in pipeline: {}".format(e))
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_ml_processor()
    sys.exit(0 if success else 1)
