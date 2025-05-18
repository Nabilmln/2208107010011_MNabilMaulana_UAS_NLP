# 🎤 Voice Chatbot UAS – Integrasi STT, Gemini LLM, dan TTS

Proyek ini adalah implementasi chatbot berbasis suara yang memungkinkan interaksi dua arah secara alami melalui web. Sistem menangkap ucapan pengguna, mengubahnya menjadi teks, merespons menggunakan model bahasa besar dari Google (Gemini API), lalu membacakan kembali respons menggunakan teknologi Text-to-Speech.

---

## 🌟 Fitur Unggulan
- **Pengenalan Suara (STT)**  
  Menggunakan `whisper.cpp` dari OpenAI untuk mentranskripsikan ucapan ke teks secara akurat.

- **Pemrosesan Bahasa (LLM)**  
  Terintegrasi dengan Google Gemini API untuk menghasilkan respons cerdas dalam Bahasa Indonesia.

- **Konversi Teks ke Suara (TTS)**  
  Menggunakan model TTS dari Coqui, dilengkapi dukungan suara bahasa Indonesia.

- **Antarmuka Web Interaktif**  
  Dibangun dengan `Gradio`, memudahkan pengujian langsung di browser tanpa setup kompleks.

---

## 🏗️ Struktur Folder

voice_chatbot_project/
│
├── app/
│ ├── main.py # Routing utama dengan FastAPI
│ ├── llm.py # Fungsi integrasi dengan Gemini API
│ ├── stt.py # Modul transkripsi menggunakan Whisper
│ ├── tts.py # Modul untuk Coqui TTS
│ ├── whisper.cpp/ # Direktori hasil clone whisper.cpp
│ └── coqui_utils/ # Konfigurasi & model Coqui
│
├── gradio_app/
│ └── app.py # UI Gradio berbasis web
│
├── .env # File konfigurasi API Key Gemini
├── requirements.txt # Daftar dependensi yang dibutuhkan

---

## ⚙️ Teknologi dan Rekomendasi
- Semua file audio menggunakan format `.wav`
- Disarankan menggunakan model Whisper: `ggml-large-v3-turbo`
- Gunakan speaker: `wibowo` dari model Coqui TTS v1.2
- Hasil dari Gemini perlu dikonversi ke bentuk fonetik sebelum dibaca oleh TTS  
  Contoh konversi: `dengan` → `dəˈnɡan`

---

## 🎓 Tujuan Proyek
Proyek ini dikembangkan sebagai bagian dari tugas akhir semester pada mata kuliah **Pemrosesan Bahasa Alami**, Semester Genap Tahun Ajaran 2024/2025.  
Proyek ini mendemonstrasikan bagaimana teknologi STT, LLM, dan TTS dapat diintegrasikan menjadi sistem chatbot suara berbasis web yang interaktif dan user-friendly.
