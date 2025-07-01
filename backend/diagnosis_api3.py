import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
import wfdb
import neurokit2 as nk
from scipy import signal
import shutil
import logging
import json

# ==============================================================================
# Inisialisasi & Pemuatan Aset yang Sudah Jadi
# ==============================================================================
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ASSETS_FOLDER = os.path.join(BASE_DIR, '../train-model') # Arahkan ke folder aset baru

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Muat semua aset yang sudah kita siapkan
try:
    model_terlatih = joblib.load(os.path.join(ASSETS_FOLDER, 'model_ekg_randomforest.joblib'))
    imputer = joblib.load(os.path.join(ASSETS_FOLDER, 'imputer.joblib'))
    with open(os.path.join(ASSETS_FOLDER, 'feature_columns.json'), 'r') as f:
        feature_columns = json.load(f)
    
    app.logger.info("✅ Semua aset (model, imputer, kolom) berhasil dimuat.")
except Exception as e:
    app.logger.error(f"❌ Gagal memuat aset saat startup: {e}")
    # Hentikan aplikasi jika aset penting tidak ada
    model_terlatih = imputer = feature_columns = None

# ==============================================================================
# Fungsi Pembantu (Sama seperti sebelumnya)
# ==============================================================================
def filter_signal(signal_data, fs):
    # ... (kode fungsi filter_signal sama persis seperti sebelumnya) ...
    lowcut, highcut = 0.5, 45.0; nyquist = 0.5 * fs
    b, a = signal.butter(2, [lowcut / nyquist, highcut / nyquist], btype='band')
    return signal.filtfilt(b, a, signal_data, axis=0)

def extract_ecg_features(record_path):
    # ... (kode fungsi extract_ecg_features sama persis seperti sebelumnya) ...
    try:
        ecg_record = wfdb.rdrecord(record_path); raw_signal = ecg_record.p_signal[:, :12]; fs = ecg_record.fs
        filtered_signal = filter_signal(raw_signal, fs)
        signals, info = nk.ecg_process(filtered_signal[:, 1], sampling_rate=fs)
        hrv_features = nk.hrv(info, sampling_rate=fs)
        return {'Rata_Rata_HR': signals['ECG_Rate'].mean(), 'HRV_SDNN': hrv_features.get('HRV_SDNN', pd.Series([np.nan])).iloc[0], 'HRV_RMSSD': hrv_features.get('HRV_RMSSD', pd.Series([np.nan])).iloc[0]}
    except Exception as e:
        app.logger.error(f"Error saat ekstraksi fitur: {e}"); return None

# ==============================================================================
# Endpoint Utama untuk Prediksi (Jauh Lebih Ringkas)
# ==============================================================================
@app.route('/predict', methods=['POST'])
def predict_ecg():
    if not all([model_terlatih, imputer, feature_columns]):
        return jsonify({"error": "Server-side error: Aset model tidak lengkap."}), 500

    # 1. Terima file & data pasien (sama seperti sebelumnya)
    # ... (kode untuk menerima file dan form data sama persis) ...
    if 'hea_file' not in request.files or 'dat_file' not in request.files: return jsonify({"error": "Input error: File .hea atau .dat tidak ditemukan."}), 400
    hea_file = request.files['hea_file']; dat_file = request.files['dat_file']
    record_name = os.path.splitext(hea_file.filename)[0]
    temp_upload_dir = os.path.join(UPLOAD_FOLDER, record_name); os.makedirs(temp_upload_dir, exist_ok=True)
    hea_file.save(os.path.join(temp_upload_dir, hea_file.filename)); dat_file.save(os.path.join(temp_upload_dir, dat_file.filename))
    record_path_for_wfdb = os.path.join(temp_upload_dir, record_name)
    try:
        age = int(request.form['age']); sex = int(request.form['sex']); smoker = request.form['smoker']
    except (KeyError, ValueError) as e: return jsonify({"error": f"Input error: Data form tidak valid: {e}"}), 400

    # 2. Ekstrak fitur sinyal
    signal_features = extract_ecg_features(record_path_for_wfdb)
    if signal_features is None:
        shutil.rmtree(temp_upload_dir)
        return jsonify({"error": "Processing error: Gagal mengekstrak fitur EKG."}), 500

    # 3. Buat DataFrame untuk data baru
    new_data = {
        'Age': age, 'Sex': sex, 'Smoker': smoker,
        'Rata_Rata_HR': signal_features['Rata_Rata_HR'], 'HRV_SDNN': signal_features['HRV_SDNN'],
        'HRV_RMSSD': signal_features['HRV_RMSSD'], 'Acute_Infarction_Localization': 'no', 
        'Additional_Diagnoses': 'no'
    }
    df_new = pd.DataFrame([new_data])

    # 4. Pra-pemrosesan yang Konsisten dan Andal
    # One-Hot Encode data baru
    df_new_encoded = pd.get_dummies(df_new)
    # Selaraskan kolom dengan data training (tambahkan kolom yg hilang, isi dengan 0)
    df_new_aligned = df_new_encoded.reindex(columns=feature_columns, fill_value=0)
    # Isi nilai NaN menggunakan imputer yang sudah dilatih
    new_data_imputed = imputer.transform(df_new_aligned)
    
    # 5. Lakukan Prediksi
    prediksi_id = model_terlatih.predict(new_data_imputed)
    prediksi_probabilitas = model_terlatih.predict_proba(new_data_imputed)

    # 6. Kirim Respons
    # Untuk mapping, kita bisa hardcode karena sudah final
    diagnosis_mapping = {
        0: 'Angina/Other Symptoms', 1: 'Bundle branch block', 2: 'Cardiomyopathy', 
        3: 'Dysrhythmia', 4: 'Heart failure', 5: 'Healthy control', 
        6: 'Myocardial hypertrophy', 7: 'Myocardial infarction', 8: 'Myocarditis', 
        9: 'Valvular heart disease'
    }
    nama_diagnosis_prediksi = diagnosis_mapping.get(int(prediksi_id[0]), "ID Tidak Dikenal")
    probabilitas_tertinggi = np.max(prediksi_probabilitas) * 100

    shutil.rmtree(temp_upload_dir) # Bersihkan file sementara
    
    return jsonify({"diagnosis": nama_diagnosis_prediksi, "confidence": round(probabilitas_tertinggi, 2)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)