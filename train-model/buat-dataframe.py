import os
import pandas as pd
import numpy as np # Berguna untuk nilai NaN
import re # Modul Regular Expression untuk parsing teks yang lebih andal

# --- (1) INISIALISASI & KONFIGURASI ---
# Ganti dengan path folder utama dataset Anda
base_path = r'C:\Users\HP\Documents\ptbdb' 
output_filename = 'metadata_klinis_ekg.csv'

# Daftar untuk menampung semua data yang berhasil di-parse
parsed_data_list = []

print(f"Memulai proses parsing dari folder: {base_path}")

# --- (2) LOOPING MELALUI SEMUA FOLDER & FILE ---
# os.walk akan secara otomatis menjelajahi semua sub-folder
for root, dirs, files in os.walk(base_path):
    for filename in files:
        # Proses hanya file yang berakhiran .hea
        if filename.endswith('.hea'):
            file_path = os.path.join(root, filename)
            
            # Ambil nama rekaman sebagai ID unik, misal: 's0010_re'
            record_name = filename.split('.')[0]
            
            # --- (3) PROSES PARSING SETIAP FILE .HEA ---
            try:
                with open(file_path, 'r') as f:
                    # Baca seluruh konten file untuk memudahkan pencarian
                    content = f.read()

                    # Siapkan dictionary untuk menampung hasil parsing file ini
                    # Default-nya semua nilai adalah NaN (Not a Number)
                    record_info = {
                        'Record': record_name,
                        'Age': np.nan,
                        'Sex': np.nan,
                        'Diagnosis': np.nan,
                        'Smoker': np.nan,
                        'Acute_Infarction_Localization': np.nan,
                        'Additional_Diagnoses': np.nan
                    }

                    # Gunakan regular expression untuk mencari dan mengekstrak data
                    # Ini lebih tangguh daripada split(':') biasa
                    
                    # Cari Usia (Age)
                    age_match = re.search(r'# age:\s*(\d+)', content)
                    if age_match:
                        record_info['Age'] = int(age_match.group(1))

                    # Cari Jenis Kelamin (Sex) dan lakukan encoding
                    sex_match = re.search(r'# sex:\s*(\w+)', content)
                    if sex_match:
                        sex_str = sex_match.group(1).lower()
                        if sex_str == 'female':
                            record_info['Sex'] = 0
                        elif sex_str == 'male':
                            record_info['Sex'] = 1
                    
                    # Cari Diagnosis Utama
                    diag_match = re.search(r'# Reason for admission:\s*(.*)', content)
                    if diag_match:
                        record_info['Diagnosis'] = diag_match.group(1).strip()
                        
                    # Cari Status Perokok (Smoker)
                    smoker_match = re.search(r'# Smoker:\s*(\w+)', content)
                    if smoker_match:
                         record_info['Smoker'] = smoker_match.group(1).lower()
                         
                    # Cari Lokasi Infark Akut
                    acute_inf_match = re.search(r'# Acute infarction \(localization\):\s*(.*)', content)
                    if acute_inf_match:
                        record_info['Acute_Infarction_Localization'] = acute_inf_match.group(1).strip()

                    # Cari Diagnosis Tambahan
                    add_diag_match = re.search(r'# Additional diagnoses:\s*(.*)', content)
                    if add_diag_match:
                        record_info['Additional_Diagnoses'] = add_diag_match.group(1).strip()

                    # Tambahkan dictionary yang sudah terisi ke dalam list utama
                    parsed_data_list.append(record_info)

            except Exception as e:
                print(f"Gagal memproses file {file_path}: {e}")

# --- (4) FINALISASI: MEMBUAT DAN MENYIMPAN DATAFRAME ---
if parsed_data_list:
    # Buat DataFrame dari list of dictionaries
    df = pd.DataFrame(parsed_data_list)
    
    # Atur urutan kolom agar lebih rapi
    column_order = [
        'Record', 'Diagnosis', 'Age', 'Sex', 'Smoker', 
        'Acute_Infarction_Localization', 'Additional_Diagnoses'
    ]
    df = df[column_order]

    # Simpan DataFrame ke file CSV
    # index=False agar nomor baris dari pandas tidak ikut tersimpan
    output_path = os.path.join(base_path, output_filename)
    df.to_csv(output_path, index=False)
    
    print("\n--- PROSES SELESAI ---")
    print(f"Berhasil memproses {len(df)} rekaman.")
    print(f"DataFrame berhasil disimpan di: {output_path}")
    print("\nContoh 5 baris pertama dari data Anda:")
    print(df.head())
else:
    print("Tidak ada file .hea yang ditemukan atau berhasil diproses.")