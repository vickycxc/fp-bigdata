import requests
import os

# Siapkan file-file dari salah satu pasien untuk diuji
# Ganti dengan path dan nama file yang benar
TEST_DATA_PATH = r'C:\Users\HP\Documents\ptbdb\patient001' 
HEA_FILE = 's0010_re.hea'
DAT_FILE = 's0010_re.dat'
XYZ_FILE = 's0010_re.xyz' # Opsional

url = 'http://127.0.0.1:5000/predict'

# Siapkan data form
form_data = {
    'age': '81',
    'sex': '0', # 0 untuk female
    'smoker': 'no'
}

# Siapkan file untuk di-upload
files = {
    'hea_file': (HEA_FILE, open(os.path.join(TEST_DATA_PATH, HEA_FILE), 'rb'), 'application/octet-stream'),
    'dat_file': (DAT_FILE, open(os.path.join(TEST_DATA_PATH, DAT_FILE), 'rb'), 'application/octet-stream'),
    'xyz_file': (XYZ_FILE, open(os.path.join(TEST_DATA_PATH, XYZ_FILE), 'rb'), 'application/octet-stream')
}

# Kirim request
try:
    response = requests.post(url, data=form_data, files=files)
    response.raise_for_status() # Akan error jika status code bukan 2xx

    # Cetak hasil
    print("Status Code:", response.status_code)
    print("Hasil Prediksi:", response.json())

except requests.exceptions.RequestException as e:
    print(f"Gagal mengirim request: {e}")
    if 'response' in locals():
        print("Response dari server:", response.text)