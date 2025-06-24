# Mengimpor library yang dibutuhkan dari PySpark
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, FloatType
# Library untuk memuat model Machine Learning yang sudah dilatih
import joblib

# Mengimpor fungsi "resep" yang telah kita buat di file terpisah
# Pastikan file feature_extractor.py ada di direktori yang sama
from feature_extractor import extract_features 

# ==============================================================================
# --- BAGIAN KONFIGURASI ---
# ==============================================================================
KAFKA_TOPIC = "ekg_topic"
KAFKA_SERVER = "localhost:9092"
# Pastikan path ke model ini benar dan file-nya ada di direktori kerja
MODEL_PATH = "model_jantung_rf.pkl" 

# ==============================================================================
# --- FUNGSI UNTUK PREDIKSI (DIJALANKAN OLEH SPARK) ---
# ==============================================================================

# Muat model ML di awal agar tidak perlu dimuat berulang kali
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    print(f"FATAL ERROR: File model '{MODEL_PATH}' tidak ditemukan!")
    print("Pastikan Anda sudah melatih model dan meletakkannya di direktori yang benar.")
    exit()

def predict_udf_func(features):
    """
    User-Defined Function (UDF) untuk melakukan prediksi menggunakan model yang sudah dimuat.
    Fungsi ini akan menerima kolom 'features' sebagai input.
    """
    # Menangani kasus jika ekstraksi fitur gagal dan menghasilkan None
    if features is None or len(features) == 0:
        return "Error: Fitur Gagal Diekstrak"
    
    try:
        # Model scikit-learn mengharapkan input 2D, jadi kita bungkus fitur dalam list
        prediction_result = model.predict([features])
        
        # Mapping hasil prediksi (angka 0, 1, 2) ke label yang bisa dibaca manusia
        # PENTING: Sesuaikan mapping ini dengan label saat Anda melatih model
        label_map = {0: 'Sehat', 1: 'Infark Miokard', 2: 'Kardiomiopati'}
        
        # Ambil hasil pertama dari array prediksi dan cari labelnya di map
        return label_map.get(prediction_result[0], "Label Tidak Dikenal")
    except Exception as e:
        return f"Error Saat Prediksi: {str(e)}"

# ==============================================================================
# --- APLIKASI UTAMA SPARK STREAMING ---
# ==============================================================================

# 1. Inisialisasi SparkSession
#    Perhatikan .config("spark.jars.packages", ...) -> ini WAJIB untuk koneksi ke Kafka
#    Sesuaikan versi '3.5.1' dengan versi Spark Anda jika perlu untuk kompatibilitas terbaik
spark = SparkSession \
    .builder \
    .appName("RealtimeEKGConsumer") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .getOrCreate()

# Definisikan skema JSON dari pesan yang dikirim oleh producer
# Skema ini HARUS SAMA PERSIS dengan struktur dictionary di producer.py
schema = StructType([
    StructField("record_name", StringType()),
    StructField("base_path", StringType())
])

# 2. Baca data dari Kafka Topic sebagai sebuah DataStream
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# 3. Decode pesan (value) dari format binary Kafka menjadi string, lalu parse sebagai JSON
value_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# 4. Terapkan UDF untuk Ekstraksi Fitur
#    Fungsi `extract_features` diimpor dari file `feature_extractor.py`
extract_features_udf = udf(extract_features, ArrayType(FloatType()))
features_df = value_df.withColumn("features", extract_features_udf(col("record_name"), col("base_path")))

# 5. Terapkan UDF untuk Prediksi
#    Fungsi `predict_udf_func` didefinisikan di atas
predict_udf = udf(predict_udf_func, StringType())
prediction_df = features_df.withColumn("prediction", predict_udf(col("features")))

# 6. Tampilkan hasilnya ke Konsol
#    Ini adalah output paling sederhana untuk debugging dan melihat hasilnya secara langsung.
#    `outputMode("update")` hanya akan menampilkan baris yang baru atau berubah.
#    `truncate=False` memastikan isi kolom tidak terpotong.
query = prediction_df \
    .writeStream \
    .outputMode("update") \
    .format("console") \
    .option("truncate", "false") \
    .start()

# Perintah ini membuat aplikasi terus berjalan dan mendengarkan data baru
query.awaitTermination()