import wfdb
import numpy as np
from scipy.signal import butter, lfilter, find_peaks

# --- INI ADALAH FUNGSI INTI (RESEP ANDA) ---
def extract_features(record_name, base_path):
    """
    Fungsi ini mengambil nama rekaman EKG, membaca filenya dari path yang diberikan,
    melakukan pra-pemrosesan, dan mengekstrak fitur-fitur numerik.

    Args:
        record_name (str): Nama rekaman (contoh: 'patient001/s0010_re').
        base_path (str): Path dasar tempat file rekaman disimpan (bisa path lokal atau HDFS).

    Returns:
        list: Sebuah list berisi fitur-fitur numerik. 
              Urutannya harus selalu sama.
              Mengembalikan None jika terjadi error.
    """
    try:
        # --- 1. MEMBACA DATA SINYAL EKG ---
        # Menggabungkan path dasar dengan nama rekaman untuk mendapatkan path lengkap
        full_path = f"{base_path}/{record_name}"
        
        # Membaca record menggunakan library wfdb
        record = wfdb.rdrecord(full_path)
        
        # Untuk kesederhanaan, kita akan analisis salah satu lead yang paling umum, yaitu Lead II.
        # Di PTB-DB, Lead II biasanya ada di indeks ke-1.
        signal = record.p_signal[:, 1]
        fs = record.fs

        # --- 2. PRA-PEMROSESAN: FILTERING NOISE ---
        # Membuat Butterworth bandpass filter untuk menghilangkan baseline wander dan noise frekuensi tinggi.
        # Frekuensi 0.5 Hz - 45 Hz adalah rentang yang umum untuk analisis QRS.
        nyquist = 0.5 * fs
        low = 0.5 / nyquist
        high = 45 / nyquist
        b, a = butter(1, [low, high], btype='band')

        # Menerapkan filter ke sinyal
        filtered_signal = lfilter(b, a, signal)

        # --- 3. DETEKSI PUNCAK R (R-PEAKS) ---
        # Mendeteksi puncak R adalah langkah kunci untuk mengukur detak jantung.
        # 'distance' memastikan kita tidak mendeteksi puncak yang terlalu berdekatan (misal, min 150ms antar detak)
        # 'height' adalah ambang batas minimal dari puncak yang dianggap sebagai R-peak.
        distance_in_samples = int(0.4 * fs) # Jarak minimal antar puncak (400ms)
        height_threshold = np.mean(filtered_signal) + 0.5 * np.std(filtered_signal)
        
        r_peaks, _ = find_peaks(filtered_signal, height=height_threshold, distance=distance_in_samples)

        # --- 4. EKSTRAKSI FITUR ---
        # Kita perlu menangani kasus jika tidak ada cukup detak jantung yang terdeteksi.
        if len(r_peaks) < 2:
            # Jika detak jantung terlalu sedikit, kita tidak bisa menghitung interval.
            # Kembalikan nilai default (misal, 0) untuk semua fitur.
            return [0.0, 0.0, 0.0, 0.0]

        # Menghitung interval R-R dalam detik
        rr_intervals = np.diff(r_peaks) / fs
        
        # Fitur 1: Rata-rata interval R-R (detik)
        mean_rr = np.mean(rr_intervals)
        
        # Fitur 2: Denyut Jantung Rata-rata (Beats Per Minute - BPM)
        heart_rate = 60 / mean_rr
        
        # Fitur 3: Standar Deviasi interval R-R (Ukuran Variabilitas Denyut Jantung - HRV)
        # SDNN (Standard Deviation of NN intervals) adalah metrik HRV yang umum. Dinyatakan dalam milidetik.
        std_rr_ms = np.std(rr_intervals) * 1000
        
        # Fitur 4: Jumlah total detak jantung yang terdeteksi
        num_peaks = len(r_peaks)

        # Mengembalikan semua fitur dalam sebuah list. PENTING: urutannya harus selalu sama!
        return [heart_rate, mean_rr, std_rr_ms, num_peaks]

    except Exception as e:
        # Jika terjadi error saat memproses satu file (misal: file tidak ditemukan, file korup),
        # kita cetak errornya dan kembalikan None agar proses Spark tidak berhenti total.
        print(f"Error processing {record_name}: {e}")
        return None