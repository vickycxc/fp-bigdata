import os
import joblib
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, FloatType, StringType, StructField, StructType
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from hdfs import InsecureClient
from feature_extractor import extract_features
from parser import parse_diagnosis_from_header
import traceback

def main():
    HDFS_URL = 'http://namenode:9870'
    HDFS_USER = 'root'
    HDFS_DATA_PATH = '/user/fp-bigdata/ptbdb_raw/'
    TRAINING_DATA_HDFS_PATH = '/user/fp-bigdata/training_data_permanent'
    
    MODEL_FILENAME = 'model_jantung_rf.pkl'
    LABEL_ENCODER_FILENAME = 'label_encoder.pkl'

    spark = SparkSession.builder.appName("InitialModelTraining_50_Data").getOrCreate()
    print("Spark Session berhasil dibuat.")

    all_records_with_diagnosis = []
    try:
        print(f"Mencoba menghubungkan ke HDFS di {HDFS_URL}...")
        client = InsecureClient(HDFS_URL, user=HDFS_USER)
        print("Berhasil terhubung ke HDFS!")

        files_in_hdfs = client.list(HDFS_DATA_PATH)
        print(f"Membaca dan mem-parsing {len(files_in_hdfs)} file dari HDFS...")
        
        for filename in files_in_hdfs:
            if filename.endswith('.hea'):
                full_path = f"{HDFS_DATA_PATH}{filename}"
                with client.read(full_path, encoding='utf-8') as reader:
                    header_content = reader.read()
                
                diagnosis = parse_diagnosis_from_header(header_content)
                if diagnosis:
                    record_name = f"{HDFS_DATA_PATH}{filename}".replace(".hea","")
                    all_records_with_diagnosis.append((record_name, diagnosis))

        if not all_records_with_diagnosis:
            raise Exception("Tidak ada diagnosis yang bisa diparsing. Periksa file .hea atau logika parser.py.")

        print(f"Total {len(all_records_with_diagnosis)} record dengan diagnosis ditemukan.")
    except Exception as e:
        print(f"Gagal memproses dari HDFS: {e}")
        traceback.print_exc()
        spark.stop()
        return

    schema = StructType([StructField("record_name", StringType()), StructField("diagnosis", StringType())])
    df_all_metadata = spark.createDataFrame(all_records_with_diagnosis, schema)
    df_50_metadata = df_all_metadata.limit(50)
    
    print(f"Mengambil {df_50_metadata.count()} data pertama untuk pelatihan awal.")
    
    HDFS_RPC_URI = f"hdfs://namenode:9000" # UDF perlu RPC URI
    extract_features_udf = udf(extract_features, ArrayType(FloatType()))
    # Di UDF, kita gunakan path lengkap karena record_name sekarang adalah path lengkap
    df_50_features = df_50_metadata.withColumn("features", extract_features_udf("record_name", HDFS_RPC_URI))
    
    pandas_df = df_50_features.toPandas().dropna(subset=['features'])

    if len(pandas_df) < 2:
        print("Tidak cukup data untuk dilatih. Proses berhenti.")
        spark.stop()
        return

    le = LabelEncoder()
    pandas_df['label_encoded'] = le.fit_transform(pandas_df['diagnosis'])
    
    X = list(pandas_df['features'])
    y = pandas_df['label_encoded']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    print("Memulai pelatihan model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("Pelatihan selesai.")
    
    predictions = model.predict(X_test)
    print("\nLaporan Klasifikasi Model Awal:")
    print(classification_report(y_test, predictions, target_names=le.classes_, zero_division=0))
    
    print("\nMenyimpan artefak...")
    joblib.dump(model, MODEL_FILENAME)
    joblib.dump(le, LABEL_ENCODER_FILENAME)
    
    print("Artefak model dan encoder disimpan secara lokal di dalam container (dan di folder proyek Anda).")

    spark.stop()
    print("\nProses pelatihan awal selesai sepenuhnya.")

if __name__ == "__main__":
    main()