# 🩺 Cardiologix
### Klasifikasi Kondisi Jantung Cerdas dari Sinyal EKG

DEMO 📷
"https://www.youtube.com/watch?v=vQV-2IFsTL8"

---

## 📌 Deskripsi Singkat

**Cardiologix** adalah sistem cerdas berbasis *big data* yang dirancang untuk menganalisis dan mengklasifikasikan sinyal Elektrokardiogram (EKG). [cite_start]Tujuan utamanya adalah membangun sebuah *pipeline* pemrosesan data untuk mendeteksi secara dini kondisi jantung seperti **Infark Miokard** dan **Kardiomiopati** dari sinyal EKG multi-lead[cite: 1, 12].

[cite_start]Sistem ini memanfaatkan data klinis dari *PTB Diagnostic ECG Database (PTBDB)* [cite: 7][cite_start], menggabungkan data demografi pasien dengan data sinyal EKG format WFDB untuk menghasilkan diagnosis akurat melalui model *machine learning* atau *deep learning*[cite: 5, 12].

---

## ✨ Fitur Utama

- [cite_start]**🩺 Klasifikasi Kondisi Jantung:** Secara otomatis mengklasifikasikan tiga kondisi utama: Infark Miokard, Kardiomiopati, dan Jantung Sehat[cite: 7, 12].
- **📂 Unggah Data Pasien:** Mendukung input data pasien berupa usia, jenis kelamin, status merokok, serta file sinyal EKG (.dat) dan file konfigurasi (.xyz).
- **📈 Visualisasi Sinyal EKG:** Menampilkan grafik sinyal EKG secara interaktif untuk dianalisis setelah data diproses.
- [cite_start]**🚀 Pipeline Big Data:** Dibangun di atas Apache Spark untuk pemrosesan data sinyal EKG yang efisien dan terdistribusi[cite: 16].
- [cite_start]**🧠 Prediksi Cerdas:** Menggunakan model *Machine Learning/Deep Learning* (seperti Random Forest, CNN, atau LSTM) untuk melakukan prediksi[cite: 14].

---

## 🧠 Analisis 5V Big Data

| Aspek | Penjelasan |
| :--- | :--- |
| **Volume** | [cite_start]Dataset sebesar **1.7 GB** (PTB Diagnostic ECG Database)[cite: 5]. |
| **Velocity** | [cite_start]Analisis data dilakukan secara *batch*, dengan potensi pengembangan untuk simulasi *real-time* menggunakan Apache Kafka & Spark Streaming[cite: 5, 18]. |
| **Variety** | [cite_start]Data terstruktur (diagnosis, demografi) dan semi-terstruktur (sinyal EKG dalam format WFDB)[cite: 5]. |
| **Veracity** | [cite_start]Menggunakan data klinis dengan diagnosis dari ahli, namun kualitas sinyal EKG memerlukan pra-pemrosesan untuk memastikan akurasi[cite: 5]. |
| **Value** | [cite_start]Memberikan nilai berupa model klasifikasi penyakit jantung yang dapat menjadi alat bantu diagnosis dan identifikasi fitur EKG penting[cite: 5]. |

---

## 🏗️ Arsitektur Proyek
(Akan diperbarui dengan diagram arsitektur proyek)

---

## ⚙️ Teknologi yang Digunakan

| Kategori | Teknologi |
| :--- | :--- |
| **Penyimpanan & Distribusi** | [cite_start]HDFS (Hadoop) [cite: 15] |
| **Pemrosesan Big Data** | [cite_start]Apache Spark (PySpark) [cite: 16] |
| **Signal Processing & ML** | [cite_start]Python, wfdb, SciPy, NumPy, Pandas, Scikit-learn, TensorFlow/Keras [cite: 17] |
| **Streaming (Opsional)** | [cite_start]Apache Kafka, Spark Streaming [cite: 18] |
| **Visualisasi Data** | [cite_start]Matplotlib, Seaborn, Chart.js [cite: 19] |
| **Antarmuka Pengguna (UI)** | HTML, CSS, JavaScript |