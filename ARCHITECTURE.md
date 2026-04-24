# Architecture Diagram - K-Means Banjir Refactored

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLASK APPLICATION (index.py)                  │
│                                                                    │
│  Routes organized by category:                                    │
│  ├── Frontend Routes (/, /hasil-cluster, /peta-bencana)          │
│  ├── Auth Routes (/login, /logout)                               │
│  ├── User Profile Routes (/setting, /contact, /dashboard)        │
│  ├── User Management Routes (/management-user, /edit/user/*)     │
│  ├── Data Management Routes (/management-data, /insert-data/*)   │
│  ├── Upload Routes (/upload-file)                                │
│  └── ML/Clustering Routes (/cluster-data, /prosess, /api/*)      │
└──────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
        ┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
        │  Services       │ │  Database    │ │  Templates   │
        │  (Modules)      │ │  ConnectionDb│ │  & Static    │
        └─────────────────┘ └──────────────┘ └──────────────┘
                    │
    ┌───────────────┼───────────────┬─────────────────┬─────────────┐
    │               │               │                 │             │
    ▼               ▼               ▼                 ▼             ▼
┌─────────────┐ ┌──────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────────┐
│   AUTH      │ │  USERS   │ │    DATA     │ │  UPLOAD    │ │ ML (⭐)      │
│  SERVICE    │ │ SERVICE  │ │  SERVICE    │ │  SERVICE   │ │  SERVICE     │
├─────────────┤ ├──────────┤ ├─────────────┤ ├────────────┤ ├──────────────┤
│ login_view()│ │list_users│ │ list_data() │ │upload_file │ │management_   │
│logout_view()│ │edit_user │ │edit_data()  │ │save_file   │ │  cluster()   │
│login_post() │ │store_user│ │insert_data()│ │            │ │sinkronasi()  │
│             │ │update_   │ │update_data()│ │            │ │process_clust │
│             │ │  user()  │ │delete_data()│ │            │ │  ering()     │
│             │ │delete_   │ │reset_data() │ │            │ │get_results() │
│             │ │  user()  │ │data_exists()│ │            │ │get_filter()  │
│             │ │          │ │             │ │            │ │              │
│ Decorators  │ │@login_   │ │@login_      │ │@login_     │ │KMeansPro-    │
│ @login_req  │ │  required│ │  required   │ │  required  │ │cessor class: │
│ @admin_req  │ │@admin_   │ │             │ │            │ │- load_data() │
│             │ │  required│ │             │ │            │ │- preprocess()│
└─────────────┘ └──────────┘ └─────────────┘ └────────────┘ │- run_kmeans()│
                                                              │- fit_kmeans()│
                                                              │- map_cluster│
                                                              │- plot_viz() │
                                                              │- process()  │
                                                              └──────────────┘
```

## 📁 Folder Structure

```
k-means-banjir/
│
├── index.py                    ← Main Flask app (refactored, 270 lines)
├── REFACTORING_SUMMARY.md      ← Summary of changes
├── QUICK_REFERENCE.md          ← Developer quick guide
│
├── services/                   ← SERVICE MODULES (NEW)
│   ├── __init__.py
│   ├── auth_service.py         ← Authentication
│   ├── user_service.py         ← User management
│   ├── data_service.py         ← Data management
│   ├── upload_service.py       ← File upload
│   ├── ml_service.py           ← ⭐ MACHINE LEARNING (Main focus)
│   ├── utils.py                ← Decorators & helpers
│   └── README.md               ← Full documentation
│
├── database/                   ← Database layer
│   ├── ConnectionDb.py
│   ├── geojson.py
│   └── Seeder.py
│
├── static/                     ← Static files
│   ├── css/
│   ├── js/
│   ├── geojson/
│   ├── upload/
│   ├── template/
│   └── image/
│
├── templates/                  ← HTML templates
│   ├── front/
│   ├── auth/
│   ├── dashboard/
│   ├── management-user/
│   ├── management-data/
│   ├── klaster/
│   ├── contact/
│   ├── peta/
│   └── profile/
│
├── algoritma/                  ← Old notebooks/algorithms
│   ├── k_means.ipynb
│   ├── two_variabel.ipynb
│   └── hasil_klaster_banjir*.csv
│
├── storage/                    ← Processing output
│   ├── sinkronasi.csv
│   ├── prosessing.csv
│   └── result.csv
│
└── ... (other files)
```

## 🔄 Request Flow Diagram

```
REQUEST
  │
  └──► index.py route handler
        │
        ├─► @login_required decorator
        │    └─► Check session['status']
        │
        ├─► @admin_required decorator (if applicable)
        │    └─► Check session['id']['role'] == 'admin'
        │
        └──► Service function call
              │
              ├──► Database operations (initDb.*)
              ├──► File operations
              │
              ├──► If ML task:
              │    └──► ml_service.py
              │         └──► KMeansProcessor class
              │              ├── load_data()
              │              ├── preprocess_data()
              │              ├── run_kmeans_steps()
              │              ├── fit_kmeans()
              │              ├── map_clusters()
              │              ├── plot_centroid_and_clusters()
              │              └── process()
              │
              └──► Return
                   ├── render_template()
                   ├── redirect()
                   ├── jsonify()
                   └── flash()
```

## 🎯 ML Pipeline Detail

```
Input: CSV File (sinkronasi.csv)
  │
  ├───► KMeansProcessor.process()
  │     │
  │     ├──► 1. load_data()
  │     │     └─► Read CSV into DataFrame
  │     │
  │     ├──► 2. preprocess_data()
  │     │     └─► MinMaxScaler normalization
  │     │         Save to: prosessing.csv
  │     │
  │     ├──► 3. run_kmeans_steps()
  │     │     └─► Manual K-Means iterations
  │     │         └─► Log each iteration:
  │     │              ├── Distance matrix
  │     │              ├── Cluster assignments
  │     │              └── Centroids
  │     │
  │     ├──► 4. fit_kmeans()
  │     │     └─► Sklearn KMeans (final)
  │     │
  │     ├──► 5. map_clusters()
  │     │     └─► Map cluster labels:
  │     │         0 → Tidak Rawan
  │     │         1 → Rawan
  │     │         2 → Sangat Rawan
  │     │         Save to: result.csv
  │     │
  │     └──► 6. plot_centroid_and_clusters()
  │           └─► Visualize clusters
  │               Save to: static/centroid_plot.png
  │
  └──► Output: result.csv + Visualizations
       ├── DataFrame with cluster labels
       ├── Centers information
       ├── Iteration logs
       └── Plot image
```

## 🔐 Access Control

```
┌─────────────────────┐
│  Public Routes      │
├─────────────────────┤
│ /                   │
│ /login              │
│ /hasil-cluster      │
│ /peta-bencana       │
│ /contact (GET)      │
└─────────────────────┘

        │
        ▼

┌─────────────────────────────────────┐
│  @login_required Routes             │
├─────────────────────────────────────┤
│ /dashboard                          │
│ /setting                            │
│ /management-data (all)              │
│ /management-user (with @admin_req)  │
│ /upload-file                        │
│ /cluster-data (all)                 │
│ /prosess                            │
│ /api/results (no decorator)         │
│ /api/filter-by/<id>                 │
│ /contact (POST)                     │
│ /sinkronasi                         │
└─────────────────────────────────────┘

        │
        ▼

┌─────────────────────┐
│  @admin_required    │  (both decorators)
├─────────────────────┤
│ /management-user    │
│ /create/user        │
│ /edit/user/<id>     │
│ /create/user/store  │
│ /update/user/<id>   │
│ /delete-user/<id>   │
└─────────────────────┘
```

## 💡 Key Improvements

```
BEFORE (Monolithic)          AFTER (Service-oriented)
─────────────────────────────────────────────────────
- 1 giant index.py          - index.py (routes only)
  (~580 lines)              - services/ (logic)
                              * auth_service.py
                              * user_service.py
                              * data_service.py
                              * upload_service.py
                              * ml_service.py
                              * utils.py

- Mixed concerns            - Separated concerns
- Hard to test              - Easy to test
- Duplicated logic          - Reusable functions
- ML code embedded          - ML isolated
- No decorators             - Decorators for access control
- Manual error handling     - Structured error handling
                            - Better documentation
                            - Ready for scaling
```

---

**Architecture Version:** 1.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2024
