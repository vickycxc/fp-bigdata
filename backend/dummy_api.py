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
    possible_diagnoses = [
        {
            "name": "Myocardial Infarction",
            "advice": "Terdeteksi indikasi kuat Serangan Jantung. Segera cari pertolongan medis darurat."
        },
        {
            "name": "Atrial Fibrillation",
            "advice": "Irama jantung tidak teratur (aritmia). Disarankan untuk konsultasi lebih lanjut dengan kardiolog."
        },
        {
            "name": "Bundle Branch Block",
            "advice": "Terdeteksi kelainan pada jalur kelistrikan jantung. Perlu evaluasi medis untuk menentukan tingkat keparahan."
        },
        {
            "name": "Cardiomyopathy",
            "advice": "Terdapat indikasi pelemahan atau penebalan otot jantung. Pemeriksaan lanjutan seperti ekokardiogram mungkin diperlukan."
        },
        {
            "name": "Healthy Control",
            "advice": "Tidak terdeteksi kelainan signifikan pada sinyal EKG. Jaga terus pola hidup sehat."
        }
    ]
    
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
