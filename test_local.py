# Impor fungsi yang baru saja kita buat
from feature_extractor import extract_features

# --- KONFIGURASI UNTUK PENGUJIAN LOKAL ---

# 1. Ganti dengan path ke direktori dataset PTB-DB di komputer LOKAL Anda
#    (cukup path ke direktori utama yang berisi folder patientxxx)
LOCAL_DATASET_PATH = r'C:\Users\HP\Documents\ptbdb'

# 2. Pilih satu nama rekaman untuk diuji
TEST_RECORD_NAME = "patient001/s0016lre" 

# --- JALANKAN PENGUJIAN ---
print(f"Menguji ekstraksi fitur untuk record: {TEST_RECORD_NAME}")
print("-" * 30)

# Panggil fungsi dengan path lokal
extracted_features = extract_features(TEST_RECORD_NAME, LOCAL_DATASET_PATH)

# Periksa dan cetak hasilnya
if extracted_features:
    print("Ekstraksi Fitur Berhasil!")
    print(f"  -> Denyut Jantung Rata-rata (BPM): {extracted_features[0]:.2f}")
    print(f"  -> Rata-rata Interval R-R (detik): {extracted_features[1]:.4f}")
    print(f"  -> HRV - SDNN (ms):              {extracted_features[2]:.2f}")
    print(f"  -> Jumlah Detak Terdeteksi:      {int(extracted_features[3])}")
else:
    print("Ekstraksi Fitur Gagal. Periksa error di atas.")