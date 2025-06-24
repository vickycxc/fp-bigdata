#!/bin/bash
# entrypoint.sh - VERSI FINAL DENGAN ERROR HANDLING & PATH FIX

# Perintah pengaman: Keluar dari skrip jika ada satu saja perintah yang gagal
set -e

# --- PERBAIKAN FINAL DI SINI ---
# Secara eksplisit menambahkan path Spark/Hadoop ke dalam PATH environment
# agar semua perintah seperti 'hdfs' dan 'spark-submit' bisa ditemukan.
export PATH=$PATH:/usr/local/spark/bin
# -----------------------------

echo "-------------------------------------"
echo "Menunggu HDFS siap (jeda 15 detik)..."
echo "-------------------------------------"
sleep 15

echo "Membuat direktori di HDFS..."
# Perintah ini sekarang akan berhasil
hdfs dfs -mkdir -p /user/fp-bigdata/ptbdb_raw

echo "-------------------------------------"
echo "Mengunggah data lokal ke HDFS di dalam Docker..."
# Perintah ini juga akan berhasil
hdfs dfs -put /data/ptbdb_raw/* /user/fp-bigdata/ptbdb_raw/

echo "-------------------------------------"
echo "Data berhasil diunggah. Menjalankan Spark Submit..."
echo "-------------------------------------"
# Perintah ini juga akan berhasil
spark-submit \
    --master local[*] \
    --py-files feature_extractor.py,parser.py \
    train_model_50.py

echo "-------------------------------------"
echo "SKRIP SELESAI. Periksa file .pkl Anda di folder proyek."
echo "-------------------------------------"