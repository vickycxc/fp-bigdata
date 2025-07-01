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
CORS(app) 

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)

# Konfigurasi Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ASSETS_FOLDER = os.path.join(BASE_DIR, '../train-model')
MODEL_PATH = os.path.join(ASSETS_FOLDER, 'model_ekg_randomforest.joblib')
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

possible_diagnosis = {
    "0": {
        "name": "Angina/Other Symptoms",
        "advice": "Terdeteksi gejala yang mirip dengan Angina (nyeri dada) atau keluhan jantung lainnya. Ini bisa menjadi tanda peringatan dari kondisi jantung yang mendasarinya. Segera konsultasikan dengan dokter untuk diagnosis yang akurat."
    },
    "1": {
        "name": "Bundle Branch Block",
        "advice": "Terdeteksi adanya kelainan atau blok pada jalur kelistrikan jantung. Kondisi ini memerlukan evaluasi medis lebih lanjut untuk mengetahui penyebab dan tingkat keparahannya."
    },
    "2": {
        "name": "Cardiomyopathy",
        "advice": "Terdapat indikasi adanya penyakit pada otot jantung (bisa berupa penebalan atau pelemahan). Disarankan untuk melakukan pemeriksaan lanjutan seperti ekokardiogram (USG jantung) dengan kardiolog."
    },
    "3": {
        "name": "Dysrhythmia",
        "advice": "Terdeteksi irama jantung yang tidak normal atau tidak teratur (Aritmia). Sebaiknya segera konsultasi dengan dokter spesialis jantung (kardiolog) untuk pemeriksaan lebih mendalam."
    },
    "4": {
        "name": "Healthy Control",
        "advice": "Tidak terdeteksi kelainan signifikan pada sinyal EKG Anda saat ini. Pertahankan pola hidup sehat dengan diet seimbang dan olahraga teratur."
    },
    "5": {
        "name": "Heart Failure",
        "advice": "Terdeteksi indikasi Gagal Jantung, yaitu kondisi di mana jantung tidak memompa darah secara efisien. Sangat penting untuk segera menemui dokter untuk penanganan dan manajemen kondisi ini."
    },
    "6": {
        "name": "Myocardial Hypertrophy",
        "advice": "Ditemukan adanya indikasi penebalan pada otot jantung (Hipertrofi). Kondisi ini seringkali terkait dengan tekanan darah tinggi dan memerlukan evaluasi oleh kardiolog."
    },
    "7": {
        "name": "Myocardial Infarction",
        "advice": "Terdeteksi indikasi kuat Serangan Jantung (Infark Miokard). Ini adalah kondisi darurat medis. SEGERA HUBUNGI AMBULANS atau cari pertolongan medis darurat terdekat."
    },
    "8": {
        "name": "Myocarditis",
        "advice": "Terdapat tanda-tanda peradangan pada otot jantung (Miokarditis). Kondisi ini serius dan memerlukan diagnosis serta penanganan medis secepatnya untuk mencegah komplikasi."
    },
    "9": {
        "name": "Valvular Heart Disease",
        "advice": "Terindikasi adanya kelainan pada katup jantung. Disarankan untuk berkonsultasi dengan dokter untuk pemeriksaan lebih lanjut, seperti ekokardiogram, guna memastikan fungsi katup."
    }
}

# ==============================================================================
# Fungsi-Fungsi Pembantu (Helper Functions)
# ==============================================================================
def filter_signal(signal_data, fs):
    lowcut, highcut = 0.5, 45.0
    nyquist = 0.5 * fs
    b, a = signal.butter(2, [lowcut / nyquist, highcut / nyquist], btype='band')
    return signal.filtfilt(b, a, signal_data, axis=0)

def extract_ecg_features(record_path):
    try:
        ecg_record = wfdb.rdrecord(record_path)
        raw_signal = ecg_record.p_signal[:, :12]
        fs = ecg_record.fs
        filtered_signal = filter_signal(raw_signal, fs)
        signals, info = nk.ecg_process(filtered_signal[:, 1], sampling_rate=fs)
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
    if model_terlatih is None or df_training is None:
        return jsonify({"error": "Server-side error: Model atau data referensi tidak berhasil dimuat."}), 500

    if 'hea_file' not in request.files or 'dat_file' not in request.files:
        return jsonify({"error": "Input error: File .hea atau .dat tidak ditemukan."}), 400
    
    hea_file = request.files['hea_file']
    dat_file = request.files['dat_file']
    record_name = os.path.splitext(hea_file.filename)[0]
    
    temp_upload_dir = os.path.join(UPLOAD_FOLDER, record_name)
    os.makedirs(temp_upload_dir, exist_ok=True)
    
    hea_file.save(os.path.join(temp_upload_dir, hea_file.filename))
    dat_file.save(os.path.join(temp_upload_dir, dat_file.filename))
    if 'xyz_file' in request.files:
        request.files['xyz_file'].save(os.path.join(temp_upload_dir, request.files['xyz_file'].filename))
    
    record_path_for_wfdb = os.path.join(temp_upload_dir, record_name)

    try:
        age = int(request.form['age'])
        sex = int(request.form['sex'])
        smoker = request.form['smoker']
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Input error: Data form tidak valid atau hilang: {e}"}), 400

    signal_features = extract_ecg_features(record_path_for_wfdb)
    if signal_features is None:
        shutil.rmtree(temp_upload_dir)
        return jsonify({"error": "Processing error: Gagal mengekstrak fitur dari sinyal EKG."}), 500

    new_data = {
        'Age': age, 'Sex': sex, 'Smoker': smoker,
        'Rata_Rata_HR': float(signal_features['Rata_Rata_HR']),
        'HRV_SDNN': float(signal_features['HRV_SDNN']),
        'HRV_RMSSD': float(signal_features['HRV_RMSSD']),
        'Acute_Infarction_Localization': 'no', 
        'Additional_Diagnoses': 'no'
    }
    print("new data: ", new_data)
    df_new = pd.DataFrame([new_data])
    
    df_train_features_only = df_training.drop(columns=['Record', 'Diagnosis'])
    df_combined = pd.concat([df_train_features_only, df_new], ignore_index=True)
    
    kolom_untuk_encode = df_combined.select_dtypes(include=['object']).columns.tolist()
    df_encoded = pd.get_dummies(df_combined, columns=kolom_untuk_encode, dummy_na=False)
    
    new_data_encoded = df_encoded.tail(1)
    
    X_training_full = df_encoded.head(len(df_training))
    imputer = SimpleImputer(strategy='median')
    imputer.fit(X_training_full)

    new_data_imputed = imputer.transform(new_data_encoded)
    
    # --- PERBAIKAN DI SINI ---
    # Ambil nama dan urutan kolom dari X_training_full, BUKAN dari model
    X_train_columns = X_training_full.columns.tolist()
    
    df_predict = pd.DataFrame(new_data_imputed, columns=X_train_columns)
    
    prediksi_id = model_terlatih.predict(df_predict)
    prediksi_probabilitas = model_terlatih.predict_proba(df_predict)

    nama_diagnosis_prediksi = possible_diagnosis[str(prediksi_id[0])]['name']
    advice_prediksi = possible_diagnosis[str(prediksi_id[0])]['advice']
    probabilitas_tertinggi = np.max(prediksi_probabilitas) * 100

    shutil.rmtree(temp_upload_dir)

    respons = {
        "diagnosis": nama_diagnosis_prediksi,
        "advice": advice_prediksi,
        "confidence": round(probabilitas_tertinggi, 2)
    }
    
    return jsonify(respons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)