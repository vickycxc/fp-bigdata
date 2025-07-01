// Menjalankan script hanya setelah seluruh halaman HTML selesai dimuat.
document.addEventListener("DOMContentLoaded", () => {
  // ==================================================================
  // 1. PENGAMBILAN ELEMEN (GET ELEMENTS)
  // ==================================================================

  // Info Pasien & Elemen yang Disembunyikan
  const patientInfoSection = document.querySelector(".patient-info-section");
  const patientAgeInput = document.getElementById("patient-age");

  // Upload File
  const fileInputDat = document.getElementById("ecg-file-dat");
  const fileInputXyz = document.getElementById("ecg-file-xyz");
  const fileInputHea = document.getElementById("ecg-file-hea"); // Tambahkan ini
  const datFileStatus = document.getElementById("dat-file-status");
  const xyzFileStatus = document.getElementById("xyz-file-status");
  const heaFileStatus = document.getElementById("hea-file-status"); // Tambahkan ini

  // Tombol & Hasil
  const processButton = document.getElementById("process-btn");
  const diagnosisResultEl = document.getElementById("diagnosis-result");
  const statusMessageEl = document.getElementById("status-pesan");

  // Grafik
  const chartCanvas = document.getElementById("ecgChart").getContext("2d");
  let ecgChart;

  // ==================================================================
  // 2. FUNGSI BARU UNTUK KONDISI TAMPILAN
  // ==================================================================
  // REVISI: Fungsi ini memeriksa apakah ketiga file sudah diunggah.
  const checkFilesAndShowNextStep = () => {
    const datFileSelected = fileInputDat.files.length > 0;
    const xyzFileSelected = fileInputXyz.files.length > 0;
    const heaFileSelected = fileInputHea.files.length > 0; // Tambahkan ini

    // Jika KETIGA file sudah terpilih...
    if (datFileSelected && xyzFileSelected && heaFileSelected) {
      // Tampilkan bagian info pasien dan tombol proses.
      patientInfoSection.classList.remove("hidden");
      processButton.classList.remove("hidden");
    } else {
      // Jika salah satu atau kedua file belum dipilih, sembunyikan lagi.
      patientInfoSection.classList.add("hidden");
      processButton.classList.add("hidden");
    }
  };

  // ==================================================================
  // 3. EVENT LISTENER UNTUK INPUT FILE (DENGAN LOGIKA BARU)
  // ==================================================================
  // REVISI: Setiap kali file berubah, panggil fungsi pengecekan.
  fileInputDat.addEventListener("change", () => {
    if (fileInputDat.files.length > 0) {
      datFileStatus.textContent = `✔️ ${fileInputDat.files[0].name}`;
    } else {
      datFileStatus.textContent = "Tidak ada file dipilih";
    }
    checkFilesAndShowNextStep(); // Panggil fungsi pengecekan
  });

  fileInputXyz.addEventListener("change", () => {
    if (fileInputXyz.files.length > 0) {
      xyzFileStatus.textContent = `✔️ ${fileInputXyz.files[0].name}`;
    } else {
      xyzFileStatus.textContent = "Tidak ada file dipilih";
    }
    checkFilesAndShowNextStep(); // Panggil fungsi pengecekan
  });

  fileInputHea.addEventListener("change", () => {
    if (fileInputHea.files.length > 0) {
      heaFileStatus.textContent = `✔️ ${fileInputHea.files[0].name}`;
    } else {
      heaFileStatus.textContent = "Tidak ada file dipilih";
    }
    checkFilesAndShowNextStep(); // Panggil fungsi pengecekan
  });

  // ==================================================================
  // 4. FUNGSI UNTUK MENGGAMBAR GRAFIK (TIDAK BERUBAH)
  // ==================================================================
  const updateChart = (signalData) => {
    if (ecgChart) {
      ecgChart.destroy();
    }

    ecgChart = new Chart(chartCanvas, {
      type: "line",
      data: {
        labels: Array.from({ length: signalData.length }, (_, i) => i + 1),
        datasets: [
          {
            label: "Sinyal EKG",
            data: signalData,
            borderColor: "#E89F71",
            backgroundColor: "rgba(232, 159, 113, 0.15)",
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            title: { display: true, text: "Amplitudo" },
          },
          x: { title: { display: true, text: "Sampel / Waktu" } },
        },
      },
    });
  };

  // ==================================================================
  // 5. FUNGSI UTAMA (SAAT TOMBOL DIKLIK - TIDAK BERUBAH)
  // ==================================================================
  const uploadAndDiagnose = async () => {
    const ageValue = patientAgeInput.value;
    const selectedGenderEl = document.querySelector(
      'input[name="gender"]:checked'
    );
    const selectedSmokerEl = document.querySelector(
      'input[name="option"]:checked'
    ); // Tambahkan ini

    // Validasi
    if (!ageValue || !selectedGenderEl || !selectedSmokerEl) {
      // Tambahkan validasi perokok
      statusMessageEl.textContent =
        "Mohon isi Usia, Jenis Kelamin, dan status Perokok.";
      statusMessageEl.style.color = "red";
      setTimeout(() => {
        statusMessageEl.textContent = "";
      }, 3000);
      return;
    }

    if (
      fileInputDat.files.length === 0 ||
      fileInputXyz.files.length === 0 ||
      fileInputHea.files.length === 0
    ) {
      // Tambahkan validasi file .hea
      statusMessageEl.textContent =
        "Silakan pilih file .dat, .xyz, dan .hea terlebih dahulu.";
      statusMessageEl.style.color = "red";
      setTimeout(() => {
        statusMessageEl.textContent = "";
      }, 3000);
      return;
    }

    // Persiapan & Pengiriman Data
    const formData = new FormData();
    formData.append("dat_file", fileInputDat.files[0]);
    formData.append("xyz_file", fileInputXyz.files[0]);
    formData.append("hea_file", fileInputHea.files[0]); // Tambahkan ini
    formData.append("age", ageValue);
    formData.append("sex", selectedGenderEl.value);
    formData.append("smoker", selectedSmokerEl.value); // Tambahkan ini

    try {
      statusMessageEl.textContent =
        "Sedang mengirim dan memproses data, mohon tunggu...";
      statusMessageEl.style.color = "var(--teks-subjudul)";
      diagnosisResultEl.textContent = "Menganalisa...";

      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: `Terjadi error di server: ${response.statusText}`,
        }));
        throw new Error(errorData.error);
      }

      const data = await response.json();

      // Menampilkan Hasil
      diagnosisResultEl.innerHTML = `
                <span class="diagnosis-main">${data.diagnosis}</span>
                <small class="diagnosis-advice">${data.advice || ""}</small>
            `;
      statusMessageEl.textContent = "Proses berhasil!";

      if (data.visualization_data && data.visualization_data.length > 0) {
        updateChart(data.visualization_data);
      }
    } catch (error) {
      console.error("Terjadi kesalahan:", error);
      statusMessageEl.textContent = `Gagal: ${error.message}`;
      statusMessageEl.style.color = "red";
      diagnosisResultEl.textContent = "Proses Gagal";
    }
  };

  // ==================================================================
  // 6. MEMASANG EVENT LISTENER PADA TOMBOL
  // ==================================================================
  processButton.addEventListener("click", (e) => {
    e.preventDefault(); // Mencegah reload halaman
    uploadAndDiagnose();
  });
});
