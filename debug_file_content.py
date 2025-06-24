# debug_file_content.py
# Tujuan: Membaca satu file dari HDFS dan mencetak isinya mentah-mentah.

from hdfs import InsecureClient
import sys
import traceback

# --- KONFIGURASI (SAMA PERSIS DENGAN SEBELUMNYA) ---
HDFS_URL = 'http://10.255.255.254:9870'
HDFS_USER = 'hadoop'

# GANTI INI DENGAN PATH FILE YANG PASTI ADA SETELAH MENJALANKAN 'hdfs dfs -ls'
# Mari kita coba file lain untuk memastikan.
FILE_TO_READ = '/user/fp-bigdata/ptbdb_raw/patient001/s0010_re.hea' 

print("--- MEMULAI DEBUGGING KONTEN FILE MENTAH ---")
print(f"Target File: {FILE_TO_READ}")

try:
    # Buat koneksi ke HDFS
    client = InsecureClient(HDFS_URL, user=HDFS_USER)
    print("Koneksi HDFS via WebHDFS berhasil.")
    
    # Baca seluruh isi file baris per baris
    with client.read(FILE_TO_READ, encoding='utf-8') as reader:
        print("\n" + "="*20)
        print("   ISI FILE BARIS PER BARIS:")
        print("="*20)
        line_number = 1
        # Loop melalui setiap baris yang dibaca dari file
        for line in reader:
            # Print nomor baris dan isi baris mentahnya (tanpa diubah)
            print(f"{line_number:03d}: {line.strip()}")
            line_number += 1
        print("="*20)
        print("   AKHIR DARI FILE")
        print("="*20 + "\n")

    print("✅ Sesi debugging pembacaan file selesai tanpa error I/O.")

except Exception as e:
    print(f"\n!!! TERJADI ERROR SAAT MEMBACA FILE: {e} !!!")
    traceback.print_exc()