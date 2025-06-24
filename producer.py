import time
from kafka import KafkaProducer
import json
import random
import pyarrow as hdfs # Library untuk koneksi ke HDFS

# --- Konfigurasi ---
# Konfigurasi Kafka
KAFKA_TOPIC = 'ekg_topic'
KAFKA_SERVER = 'localhost:9092'

# Konfigurasi koneksi HDFS
HDFS_HOST = 'localhost'
HDFS_PORT = 9000  # Ganti jika port NameNode Anda berbeda (misal: 8020)
HDFS_USER = 'vicky' # Ganti dengan username Hadoop Anda jika perlu
# Direktori di HDFS yang berisi dataset PTBDB
HDFS_DATA_PATH = '/user/fp-bigdata/ptbdb_raw/'

# --- Inisialisasi Producer Kafka ---
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Producer siap untuk streaming data dari HDFS...")
print("-" * 50)

try:
    # 1. Menghubungkan ke HDFS
    print(f"Menghubungkan ke HDFS di hdfs://{HDFS_HOST}:{HDFS_PORT}")
    fs = hdfs.connect(host=HDFS_HOST, port=HDFS_PORT, user=HDFS_USER)
    print("Berhasil terhubung ke HDFS.")

    # 2. Dapatkan daftar semua file .hea dari direktori HDFS
    # fs.ls() akan me-list semua file dan direktori di path yang diberikan
    # Kita akan filter untuk hanya mengambil file .hea
    all_files_info = fs.ls(HDFS_DATA_PATH, detail=True)
    
    # Ekstrak nama record dari path lengkap HDFS
    # Contoh: dari 'hdfs://.../ptbdb_raw/patient001/s0010_re.hea'
    # kita ingin mendapatkan 'patient001/s0010_re'
    all_records = []
    for info in all_files_info:
        if info['kind'] == 'file' and info['name'].endswith('.hea'):
            full_path = info['name']
            # Menghapus prefix path utama dan ekstensi .hea
            record_name = full_path.replace(f"hdfs://{HDFS_HOST}:{HDFS_PORT}{HDFS_DATA_PATH}", "").replace(".hea", "")
            all_records.append(record_name)

    if not all_records:
        raise Exception(f"Tidak ada file .hea yang ditemukan di HDFS path: {HDFS_DATA_PATH}")

    print(f"Ditemukan total {len(all_records)} rekaman EKG di HDFS untuk di-streaming.")
    
    # Acak urutan rekaman agar terasa seperti data real-time
    random.shuffle(all_records)

    # 3. Loop melalui setiap nama rekaman
    for record_name in all_records:
        
        # 4. Buat dan kirim pesan ke Kafka
        # base_path sekarang adalah path HDFS
        base_path_for_message = f"hdfs://{HDFS_HOST}:{HDFS_PORT}{HDFS_DATA_PATH.rstrip('/')}"
        
        message = {
            'record_name': record_name,
            'base_path': base_path_for_message
        }
        
        print(f"Mengirim data untuk record HDFS: {record_name}")
        producer.send(KAFKA_TOPIC, message)
        producer.flush()
        
        # 5. Jeda selama 1 detik
        time.sleep(1)

    print("-" * 50)
    print("Semua data dari HDFS telah berhasil di-streaming.")

except Exception as e:
    print(f"Terjadi error: {e}")