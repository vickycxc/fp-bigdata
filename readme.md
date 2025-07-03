# 🩺 Cardiologix
### Klasifikasi Kondisi Jantung Cerdas dari Sinyal EKG

**DEMO 📷**
(Link ke Video YouTube Anda)

---
## 📌 Deskripsi Singkat
**Cardiologix** adalah sistem cerdas berbasis *big data* yang menerapkan pipeline pemrosesan data untuk menganalisis dan mengklasifikasikan sinyal Elektrokardiogram (EKG) secara *real-time*. Sistem ini mampu mendeteksi berbagai kondisi jantung, seperti **Infark Miokard** dan **Kardiomiopati**, langsung dari data mentah EKG.

Dengan mengintegrasikan model *Random Forest* yang telah dilatih pada *PTB Diagnostic ECG Database (PTBDB)*, Cardiologix menggabungkan data demografi pasien dengan fitur-fitur sinyal yang diekstrak secara otomatis untuk menghasilkan diagnosis yang cepat dan akurat.

---
## ✨ Fitur Utama
- **🧠 Prediksi Berbasis Model Machine Learning:** Menggunakan model `Random Forest` yang telah dilatih untuk secara otomatis mengklasifikasikan berbagai kondisi jantung, termasuk:
    - Infark Miokard (Serangan Jantung)
    - Kardiomiopati
    - Gagal Jantung
    - Aritmia (Dysrhythmia)
    - Penyakit Katup Jantung
    - Miokarditis
    - Kontrol Sehat
- **⚙️ Ekstraksi Fitur Sinyal Otomatis:** Secara otomatis memproses file sinyal EKG mentah (`.dat`, `.hea`) menggunakan `NeuroKit2` dan `WFDB` untuk mengekstrak fitur-fitur vital seperti *Heart Rate (HR)* dan *Heart Rate Variability (HRV)*.
- **📂 Input Data Lengkap & Realistis:** Mendukung input data pasien (usia, jenis kelamin, status merokok) dan file EKG standar medis (`.hea`, `.dat`, `.xyz`) untuk diproses oleh backend.
- **📊 Respons Akurat:** Memberikan hasil prediksi berupa nama diagnosis beserta tingkat keyakinan (*confidence*) dalam format persentase.
- **📈 Visualisasi Sinyal EKG:** Menampilkan grafik sinyal EKG secara interaktif menggunakan Chart.js setelah data berhasil diproses.

---
## 🧠 Analisis 5V Big Data

| Aspek | Penjelasan |
| :--- | :--- |
| **Volume** | Dataset sebesar **1.7 GB** (PTB Diagnostic ECG Database). |
| **Velocity** | Analisis data dilakukan secara *batch*, dengan potensi pengembangan untuk simulasi *real-time* menggunakan Apache Kafka & Spark Streaming. |
| **Variety** | Data terstruktur (diagnosis, demografi) dan semi-terstruktur (sinyal EKG dalam format WFDB). |
| **Veracity** | Menggunakan data klinis dengan diagnosis dari ahli, namun kualitas sinyal EKG memerlukan pra-pemrosesan untuk memastikan akurasi. |
| **Value** | Memberikan nilai berupa model klasifikasi penyakit jantung yang dapat menjadi alat bantu diagnosis dan identifikasi fitur EKG penting. |

---
## 🏗️ Arsitektur & Alur Kerja Proyek
Sistem ini bekerja dengan alur yang jelas, dari input pengguna hingga output berupa diagnosis.

1.  **Input Pengguna (Frontend):** Pengguna memasukkan data demografi dan mengunggah file sinyal EKG (`.hea`, `.dat`) melalui antarmuka web.
2.  **Penerimaan Data (Backend Flask):** Server Flask menerima data dan file melalui endpoint `/predict` dan menyimpannya sementara.
3.  **Ekstraksi Fitur (Signal Processing):** Sistem menggunakan library `wfdb` dan `neurokit2` untuk membaca sinyal, melakukan filtering, dan mengekstrak fitur-fitur penting (rata-rata detak jantung, HRV, dll.).
4.  **Pra-pemrosesan Data:** Data demografi dan fitur sinyal yang baru diekstrak digabungkan, lalu formatnya disesuaikan (melalui *one-hot encoding*) agar cocok dengan data saat melatih model.
5.  **Prediksi (Machine Learning):** Data yang siap dimasukkan ke dalam model `Random Forest` (`.joblib`) yang telah dimuat sebelumnya untuk menghasilkan prediksi.
6.  **Pengiriman Respons:** Hasil prediksi (diagnosis dan tingkat keyakinan) dikemas dalam format JSON dan dikirim kembali ke frontend untuk ditampilkan.

---
## ⚙️ Teknologi yang Digunakan
Berikut adalah daftar teknologi yang digunakan dalam implementasi saat ini serta yang direncanakan untuk skala lebih besar.

| Kategori | Teknologi |
| :--- | :--- |
| **Backend & API Server** | Flask, Flask-CORS |
| **Machine Learning & Model**| Scikit-learn, Joblib, Pandas, NumPy |
| **Pemrosesan Sinyal** | WFDB, NeuroKit2, SciPy |
| **Big Data & Distribusi (Scope)** | Apache Spark, HDFS (Hadoop), Apache Kafka |
| **Antarmuka Pengguna (UI)** | HTML, CSS, JavaScript, Chart.js |
| **Bahasa Utama** | Python |

VIDEO DEMONSTRASI: https://youtu.be/SQ9wd8vvA6c?si=AwAWvWJz3tDJQNlG