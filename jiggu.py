import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import altair as alt
import numpy as np

# Konfigurasi halaman
st.set_page_config(layout="wide", page_title="Dashboard Produk")

# CSS untuk mempercantik tampilan
st.markdown("""
<style>
    .main {
        padding: 2rem;
        background-color: #f0f2f6;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .sidebar .sidebar-content, .main .block-container {
        padding: 2rem 1rem;
    }
    h1, .sidebar .sidebar-content h1 {
        color: #0e1117;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #4e8cff;
    }
    h2, .sidebar .sidebar-content h2 {
        color: #ff6347;
        font-family: 'Helvetica Neue', sans-serif;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stSelectbox, .stMultiSelect, .sidebar .sidebar-content .stSelectbox, .sidebar .sidebar-content .stMultiSelect {
        background-color: white;
        border-radius: 5px;
        padding: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton>button, .sidebar .sidebar-content .stButton>button {
        background-color: #4e8cff;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .stButton>button:hover, .sidebar .sidebar-content .stButton>button:hover {
        background-color: #3a7bd5;
    }
    .dataframe {
        font-family: Arial, sans-serif;
        font-size: 12px;
        border-collapse: collapse;
        border: none;
        margin-top: 1rem;
    }
    .dataframe th {
        background-color: #4e8cff;
        color: white;
        padding: 10px;
    }
    .dataframe td {
        background-color: white;
        padding: 8px;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .stPlotlyChart {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)
# Judul dashboard
st.title("Dashboard Analisis Produk")

# Sidebar
with st.sidebar:
    st.image("WhatsApp Image 2024-07-17 at 11.47.17.jpeg", width=200)
    st.title("Filter Data")
    uploaded_file = st.file_uploader("Unggah File Data", type=["txt", "csv"])

# Main content
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".txt"):
            data = pd.read_csv(uploaded_file, sep=';')
        elif uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file, sep=";")
        else:
            st.error("Format file tidak didukung. Mohon gunakan file .txt atau .csv.")
    except Exception as e:
        st.error(f"Kesalahan dalam membaca file: {e}")
else:
    st.warning("Mohon unggah file data terlebih dahulu.")

if 'data' in locals():
    with st.sidebar:
        kategori = st.multiselect("Pilih Kategori", data['kategori'].unique(), default=data['kategori'].unique())
    
    if not kategori:
        st.warning("Silahkan pilih setidaknya satu kategori.")
        st.stop()
    filtered_data = data[data['kategori'].isin(kategori)]
    
     #kolom persentase
    filtered_data['persentase_terjual'] = round((filtered_data['terjual'] / filtered_data['stok_awal'] * 100), 3)

    
 # Pilih fitur untuk clustering
    features = ['stok_awal', 'persentase_terjual']

    # Clustering
    st.subheader("Clustering Produk dengan K-Means")
    features = ['stok_awal', 'persentase_terjual']
    num_clusters = 3

    np.random.seed(74)
    data_array = filtered_data[features].values
    random_indices = np.random.choice(data_array.shape[0], num_clusters, replace=False)
    initial_centroids = data_array[random_indices]

    kmeans = KMeans(n_clusters=num_clusters, init=initial_centroids, n_init=3, random_state=13)
    cluster_labels = kmeans.fit_predict(filtered_data[features])
    filtered_data['cluster'] = cluster_labels + 1

    # Tampilkan hasil clustering dalam expander
    with st.expander("Lihat Hasil Clustering"):
        st.write("Rata-rata Fitur per Cluster:")
        cluster_stats = filtered_data.groupby('cluster')[features].mean()
        st.dataframe(cluster_stats)

        st.write("Nama Produk per Cluster:")
        for cluster in cluster_stats.index:
            st.write(f"Cluster {cluster}:")
            cluster_products = filtered_data[filtered_data['cluster'] == cluster]['nama_produk'].tolist()
            st.write(", ".join(cluster_products[:50]))
            if len(cluster_products) > 50:
                st.write(f"... dan {len(cluster_products) - 50} produk lainnya.")
    
    with st.expander("Nama Produk Per Cluster"):
        st.subheader("Visualisasi Clustering ")
        for cluster in range(1, num_clusters + 1):
            cluster_data = filtered_data[filtered_data['cluster'] == cluster]
            st.write(f"Cluster {cluster}:")
            st.write(cluster_data[['nama_produk', 'stok_awal', 'stok_akhir']])

    
    # Tabel data
    st.subheader("Tabel Data Produk")
    st.dataframe(filtered_data[['data_ke', 'nama_produk', 'kategori', 'cluster']], height=400)

    # Diagram
    st.subheader("Visualisasi Stok Akhir Produk")
    chart_type = st.selectbox("Pilih Jenis Diagram", ["Batang", "Garis", "Titik"])

    chart_data = filtered_data[['nama_produk', 'stok_akhir']].sort_values('stok_akhir', ascending=False).head(20)

    base_chart = alt.Chart(chart_data).encode(
        x='stok_akhir:Q',
        y=alt.Y('nama_produk:N', sort='-x')
    ).properties(
        width=700,
        height=400
    )

    if chart_type == "Batang":
        chart = base_chart.mark_bar()
    elif chart_type == "Garis":
        chart = base_chart.mark_line()
    else:
        chart = base_chart.mark_point()

    st.altair_chart(chart, use_container_width=True)


# Footer
st.markdown("---")
st.markdown("Data Stok JigguShop")
st.markdown("Cluster 1 : Tinggi Peminat")
st.markdown("Cluster 2 : Kurang Peminat")
st.markdown("Cluster 3 : Jarang Peminat") 
