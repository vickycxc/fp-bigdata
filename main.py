import wfdb
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter

# Ganti dengan path ke salah satu record di komputer LOKAL Anda
record_path = r'C:\Users\HP\Documents\ptbdb\patient001\s0010_re'

# 1. Baca record menggunakan wfdb
record = wfdb.rdrecord(record_path)
# Ambil sinyal dari lead II (kolom ke-1)
signal_lead_II = record.p_signal[:, 1] 
fs = record.fs # Frekuensi sampling

# 2. Visualisasi sinyal mentah (5 detik pertama)
plt.figure(figsize=(15, 4))
plt.plot(signal_lead_II[:fs*5])
plt.title(f"Sinyal EKG Mentah dari {record.record_name} - Lead II")
plt.show()

# 3. Lakukan filtering (contoh sederhana)
# ... kode filtering menggunakan scipy ...

# 4. Lakukan deteksi puncak R (contoh sederhana, ada library yg lebih canggih)
# ... kode deteksi puncak R ...

# 5. Ekstrak fitur (contoh: hitung rata-rata interval R-R)
# ... kode ekstraksi fitur ...