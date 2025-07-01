from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/diagnose_ecg_signals', methods=['GET', 'POST'])
def get_dummy_diagnosis():
    """
    Endpoint ini akan memberikan hasil diagnosa EKG palsu secara acak
    dari daftar yang lebih komprehensif.
    """
    
    # REVISI: Daftar kemungkinan diagnosa yang lebih beragam dan realistis
    possible_diagnoses = {
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
    
    # Pilih salah satu diagnosa secara acak
    selected_diagnosis_info = random.choice(possible_diagnoses)
    
    # Hasilkan data lainnya seperti sebelumnya
    dummy_confidence = round(random.uniform(0.85, 0.99), 2)
    dummy_visualization_data = [random.uniform(-0.5, 1.5) for _ in range(250)]
    
    response_data = {
        "diagnosis": selected_diagnosis_info["name"],
        "advice": selected_diagnosis_info["advice"],
        "confidence": dummy_confidence,
        "visualization_data": dummy_visualization_data
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    # Pastikan server di-restart setelah Anda menyimpan perubahan ini.
    app.run(debug=True, port=5000)
