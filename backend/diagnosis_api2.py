import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
import wfdb
import neurokit2 as nk
from scipy import signal
from sklearn.impute import SimpleImputer
import shutil
import logging

# ==============================================================================
# Inisialisasi Aplikasi Flask & Konfigurasi Awal
# ==============================================================================
app = Flask(__name__)
CORS(app) # Mengizinkan akses dari berbagai sumber (misal: frontend React/Vue)

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)

# Konfigurasi Path (Gunakan path relatif agar portabel)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ASSETS_FOLDER = os.path.join(BASE_DIR, '../train-model')
MODEL_PATH = os.path.join(ASSETS_FOLDER, 'model_ekg_randomforest.joblib')

# --- PERUBAHAN DI SINI ---
DATA_PATH = os.path.join(ASSETS_FOLDER, 'dataset_final_untuk_ml_final.csv')

# Pastikan folder upload ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Muat model dan data training SEKALI SAJA saat aplikasi pertama kali dijalankan
try:
    model_terlatih = joblib.load(MODEL_PATH)
    df_training = pd.read_csv(DATA_PATH)
    app.logger.info("✅ Model dan data training referensi berhasil dimuat saat startup.")
except Exception as e:
    app.logger.error(f"❌ Gagal memuat model atau data training saat startup: {e}")
    model_terlatih = None
    df_training = None

# ==============================================================================
# Fungsi-Fungsi Pembantu (Helper Functions)
# ==============================================================================

def filter_signal(signal_data, fs):
    """Fungsi untuk menerapkan filter band-pass ke sinyal."""
    lowcut, highcut = 0.5, 45.0
    nyquist = 0.5 * fs
    b, a = signal.butter(2, [lowcut / nyquist, highcut / nyquist], btype='band')
    return signal.filtfilt(b, a, signal_data, axis=0)

def extract_ecg_features(record_path):
    """Mengekstrak fitur sinyal EKG dari file yang diberikan."""
    try:
        # wfdb.rdrecord akan membaca .hea dan .dat/.xyz secara otomatis
        ecg_record = wfdb.rdrecord(record_path)
        raw_signal = ecg_record.p_signal[:, :12] # Ambil 12 lead utama
        fs = ecg_record.fs

        filtered_signal = filter_signal(raw_signal, fs)
        signals, info = nk.ecg_process(filtered_signal[:, 1], sampling_rate=fs) # Menggunakan lead II
        hrv_features = nk.hrv(info, sampling_rate=fs)

        fitur = {
            'Rata_Rata_HR': signals['ECG_Rate'].mean(),
            'HRV_SDNN': hrv_features.get('HRV_SDNN', pd.Series([np.nan])).iloc[0],
            'HRV_RMSSD': hrv_features.get('HRV_RMSSD', pd.Series([np.nan])).iloc[0]
        }
        return fitur
    except Exception as e:
        app.logger.error(f"Error saat ekstraksi fitur: {e}")
        return None

# ==============================================================================
# Endpoint Utama untuk Prediksi
# ==============================================================================
@app.route('/predict', methods=['POST'])
def predict_ecg():
    """Endpoint untuk menerima file EKG dan data pasien, lalu mengembalikan prediksi."""
    if model_terlatih is None or df_training is None:
        return jsonify({"error": "Server-side error: Model atau data referensi tidak berhasil dimuat."}), 500

    # --- 1. Menerima dan Menyimpan File ---
    if 'hea_file' not in request.files or 'dat_file' not in request.files:
        return jsonify({"error": "Input error: File .hea atau .dat tidak ditemukan."}), 400
    
    hea_file = request.files['hea_file']
    dat_file = request.files['dat_file']
    xyz_file = request.files.get('xyz_file') # Opsional

    record_name = os.path.splitext(hea_file.filename)[0]
    
    # Simpan file-file tersebut sementara ke folder 'uploads'
    temp_upload_dir = os.path.join(UPLOAD_FOLDER, record_name)
    os.makedirs(temp_upload_dir, exist_ok=True)
    
    hea_path = os.path.join(temp_upload_dir, hea_file.filename)
    dat_path = os.path.join(temp_upload_dir, dat_file.filename)
    hea_file.save(hea_path)
    dat_file.save(dat_path)
    if xyz_file:
        xyz_file.save(os.path.join(temp_upload_dir, xyz_file.filename))
    
    record_path_for_wfdb = os.path.join(temp_upload_dir, record_name)

    # --- 2. Menerima Data Pasien ---
    try:
        age = int(request.form['age'])
        sex = int(request.form['sex']) # Asumsi 0: female, 1: male
        smoker = request.form['smoker'] # Asumsi 'yes' atau 'no'
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Input error: Data form tidak valid atau hilang: {e}"}), 400

    # --- 3. Ekstraksi Fitur Sinyal ---
    signal_features = extract_ecg_features(record_path_for_wfdb)
    if signal_features is None:
        shutil.rmtree(temp_upload_dir) # Bersihkan file
        return jsonify({"error": "Processing error: Gagal mengekstrak fitur dari sinyal EKG."}), 500

    # --- 4. Membuat DataFrame untuk Data Baru ---
    new_data = {
        'Age': age, 'Sex': sex, 'Smoker': smoker,
        'Rata_Rata_HR': signal_features['Rata_Rata_HR'],
        'HRV_SDNN': signal_features['HRV_SDNN'],
        'HRV_RMSSD': signal_features['HRV_RMSSD'],
        'Acute_Infarction_Localization': 'no', 
        'Additional_Diagnoses': 'no'
    }
    df_new = pd.DataFrame([new_data])

    # --- 5. Proses Ulang Data Baru agar Sesuai Format Training ---
    df_train_features = df_training.drop(columns=['Record', 'Diagnosis'])
    df_combined = pd.concat([df_train_features, df_new], ignore_index=True)
    
    kolom_untuk_encode = df_combined.select_dtypes(include=['object']).columns.tolist()
    df_encoded = pd.get_dummies(df_combined, columns=kolom_untuk_encode, dummy_na=False)
    
    new_data_encoded = df_encoded.tail(1)

    X_train_columns = model_terlatih.feature_names_in_
    new_data_aligned = pd.DataFrame(columns=X_train_columns)
    new_data_aligned = pd.concat([new_data_aligned, new_data_encoded]).fillna(0)
    
    df_predict = new_data_aligned[X_train_columns]

    # --- 6. Lakukan Prediksi ---
    prediksi_id = model_terlatih.predict(df_predict)
    prediksi_probabilitas = model_terlatih.predict_proba(df_predict)

    # --- 7. Format dan Kirim Respons ---
    df_training['Diagnosis_ID'] = df_training['Diagnosis'].astype('category').cat.codes
    diagnosis_mapping = dict(enumerate(df_training['Diagnosis'].astype('category').cat.categories))
    
    nama_diagnosis_prediksi = diagnosis_mapping.get(prediksi_id[0], "ID Tidak Dikenal")
    probabilitas_tertinggi = np.max(prediksi_probabilitas) * 100

    shutil.rmtree(temp_upload_dir) # Bersihkan file setelah selesai

    respons = {
        "diagnosis": nama_diagnosis_prediksi,
        "confidence": round(probabilitas_tertinggi, 2)
    }
    
    return jsonify(respons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)