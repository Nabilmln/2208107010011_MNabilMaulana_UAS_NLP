import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
from datetime import datetime
import base64

def voice_chat(audio, log_state=""):
    if audio is None:
        return None, "Transkrip tidak tersedia", "Transkrip tidak tersedia", "No audio provided.", "loading"
    
    log_messages = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Menerima file audio Anda..."]

    # Unpack audio tuple
    sr, audio_data = audio
    log_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Audio disimpan sementara untuk diproses.")

    # Save as .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        scipy.io.wavfile.write(tmpfile.name, sr, audio_data)
        audio_path = tmpfile.name

    # Send to FastAPI endpoint
    with open(audio_path, "rb") as f:
        files = {"file": ("voice.wav", f, "audio/wav")}
        log_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mengirim audio ke server untuk transkripsi...")
        response = requests.post("http://localhost:8000/voice-chat", files=files)

    # Clean up temporary file
    try:
        os.unlink(audio_path)
    except:
        pass

    if response.status_code == 200:
        response_data = response.json()
        log_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Audio berhasil ditranskripsi: {response_data['input_transcript']}")
        log_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Menghasilkan respons AI...")
        
        # Save audio content from base64
        output_audio_path = os.path.join(tempfile.gettempdir(), "tts_output.wav")
        audio_content = base64.b64decode(response_data["audio_content"])
        with open(output_audio_path, "wb") as f:
            f.write(audio_content)
        log_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Respons audio disimpan dan siap diputar.")
        return (
            output_audio_path,
            response_data["input_transcript"],
            response_data["output_transcript"],
            "\n".join(log_messages),
            ""  # Clear loading state
        )
    else:
        log_messages.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Gagal memproses audio: {response.json().get('error', 'Unknown error')}")
        return None, "Transkrip tidak tersedia", "Transkrip tidak tersedia", "\n".join(log_messages), ""

def clear_inputs():
    return None, None, "Transkrip tidak tersedia", "Transkrip tidak tersedia", "", ""

# Custom CSS (unchanged from previous version)
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

body {
    background: linear-gradient(180deg, #1e2a44 0%, #2e3b55 100%);
    font-family: 'Poppins', sans-serif;
    color: #ffffff;
}

.gradio-container {
    max-width: 1200px !important;
    margin: 2rem auto;
    background: transparent;
}

h1 {
    font-size: 2.5rem;
    font-weight: 600;
    color: #ff6f61;
    text-align: center;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 8px rgba(255, 111, 97, 0.5);
}

h3 {
    font-size: 1.2rem;
    color: #b0c4de;
    text-align: center;
    margin-bottom: 2rem;
}

.input-card, .output-card, .log-card {
    background: #0b0f19;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.2);
    margin-bottom: 1.5rem;
    width: 100%;
}

.input-card {
    border-left: 4px solid #ff6f61;
}

.output-card {
    border-left: 4px solid #00b7eb;
}

.log-card {
    border-left: 4px solid #10b981;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-icon {
    width: 28px;
    height: 28px;
    background: #2e3b55;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px;
}

.card-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0;
}

.input-card .card-title {
    color: #ff6f61;
}

.output-card .card-title {
    color: #00b7eb;
}

.log-card .card-title {
    color: #10b981;
}

.audio-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    position: relative;
}

.audio-input label, .audio-output label {
    display: none !important;
}

.waveform {
    width: 100%;
    height: 60px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    position: relative;
    margin-bottom: 1rem;
    overflow: hidden;
}

.input-card .waveform {
    border: 1px solid rgba(255, 111, 97, 0.2);
}

.output-card .waveform {
    border: 1px solid rgba(0, 183, 235, 0.2);
}

.wave-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.wave-line::before {
    content: "";
    width: 200%;
    height: 100%;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 60'%3E%3Cpath d='M0,30 Q20,10 40,30 T80,30 T120,30 T160,30 T200,30' stroke='%23ff6f61' fill='none' stroke-width='2'/%3E%3C/svg%3E") repeat-x;
    background-size: 200px 60px;
    position: absolute;
    animation: waveMove 1.5s linear infinite;
}

.output-card .wave-line::before {
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 60'%3E%3Cpath d='M0,30 Q20,10 40,30 T80,30 T120,30 T160,30 T200,30' stroke='%2300b7eb' fill='none' stroke-width='2'/%3E%3C/svg%3E") repeat-x;
}

.input-card .recording .wave-line::before,
.output-card .playing .wave-line::before {
    animation: waveMove 1.5s linear infinite, wavePulse 0.5s ease-in-out infinite alternate;
}

@keyframes waveMove {
    0% { transform: translateX(0); }
    100% { transform: translateX(-200px); }
}

@keyframes wavePulse {
    0% { transform: translateX(0) scaleY(1); }
    100% { transform: translateX(0) scaleY(1.2); }
}

.audio-input .wrap, .audio-output .wrap {
    background: transparent !important;
    border: none !important;
}

.audio-input audio, .audio-output audio {
    width: 100%;
}

.buttons-container {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.gr-button.submit {
    background: #ff6f61;
    color: white !important;
    border: none !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 1rem;
    font-weight: 600;
    flex: 1;
    transition: all 0.2s ease;
}

.gr-button.submit:hover {
    background: #ff5a4c;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 111, 97, 0.4);
}

.gr-button.submit[aria-disabled="true"] {
    background: #ff6f61 !important;
    opacity: 0.7;
    cursor: not-allowed;
}

.gr-button.clear {
    background: transparent;
    color: #b0c4de !important;
    border: 1px solid #b0c4de !important;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 1rem;
    font-weight: 600;
    flex: 1;
    transition: all 0.2s ease;
}

.gr-button.clear:hover {
    background: rgba(176, 196, 222, 0.1);
    transform: translateY(-2px);
}

.transcript-container {
    margin-top: 1.5rem;
    background: rgba(11, 15, 25, 0.6);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.input-card .transcript-container {
    border-left: 2px solid #ff6f61;
}

.output-card .transcript-container {
    border-left: 2px solid #00b7eb;
}

.log-card .transcript-container {
    border-left: 2px solid #10b981;
}

.transcript-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.transcript-icon {
    width: 16px;
    height: 16px;
}

.input-card .transcript-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #ff6f61;
    margin: 0;
}

.output-card .transcript-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #00b7eb;
    margin: 0;
}

.log-card .transcript-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #10b981;
    margin: 0;
}

.transcript-content {
    font-size: 0.9rem;
    color: #b0c4de;
    line-height: 1.5;
}

.log-content {
    font-size: 0.9rem;
    color: #b0c4de;
    line-height: 1.5;
    max-height: 200px;
    overflow-y: auto;
    white-space: pre-wrap;
}

.loading-spinner {
    display: none;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 4px solid #00b7eb;
    border-top: 4px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.output-card.loading .loading-spinner {
    display: block;
}

.output-card.loading .waveform,
.output-card.loading .audio-output {
    opacity: 0.3;
}

@keyframes spin {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}

#particles {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
}

@media (max-width: 768px) {
    .input-card, .output-card, .log-card {
        margin-bottom: 1.5rem;
    }
}
"""

# Gradio UI
with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
    gr.HTML("""
        <div id="particles"></div>
        <script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
        <script>
            particlesJS("particles", {
                "particles": {
                    "number": {
                        "value": 60,
                        "density": {
                            "enable": true,
                            "value_area": 1000
                        }
                    },
                    "color": {
                        "value": ["#ff6f61", "#00b7eb"]
                    },
                    "shape": {
                        "type": "circle",
                        "stroke": {
                            "width": 0,
                            "color": "#000000"
                        }
                    },
                    "opacity": {
                        "value": 0.3,
                        "random": true
                    },
                    "size": {
                        "value": 3,
                        "random": true
                    },
                    "line_linked": {
                        "enable": true,
                        "distance": 150,
                        "color": "#4a5568",
                        "opacity": 0.2,
                        "width": 1
                    },
                    "move": {
                        "enable": true,
                        "speed": 1.5,
                        "direction": "none",
                        "random": false,
                        "straight": false,
                        "out_mode": "out",
                        "bounce": false
                    }
                },
                "interactivity": {
                    "detect_on": "canvas",
                    "events": {
                        "onhover": {
                            "enable": true,
                            "mode": "grab"
                        },
                        "onclick": {
                            "enable": false
                        },
                        "resize": true
                    }
                },
                "retina_detect": true
            });

            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => {
                    const audioInput = document.querySelector('.audio-input');
                    if (audioInput) {
                        const micButton = audioInput.querySelector('button');
                        if (micButton) {
                            const inputWaveform = document.querySelector('.input-card .waveform');
                            micButton.addEventListener('click', () => {
                                if (micButton.textContent === 'Stop') {
                                    inputWaveform.classList.add('recording');
                                } else {
                                    inputWaveform.classList.remove('recording');
                                }
                            });
                        }
                    }
                    
                    const audioOutput = document.querySelector('.audio-output');
                    if (audioOutput) {
                        const audioElement = audioOutput.querySelector('audio');
                        const outputWaveform = document.querySelector('.output-card .waveform');
                        const outputCard = document.querySelector('.output-card');
                        
                        if (audioElement) {
                            audioElement.addEventListener('play', () => {
                                outputWaveform.classList.add('playing');
                                outputCard.classList.remove('loading');
                            });
                            audioElement.addEventListener('pause', () => {
                                outputWaveform.classList.remove('playing');
                            });
                            audioElement.addEventListener('ended', () => {
                                outputWaveform.classList.remove('playing');
                            });
                        }
                    }

                    const submitButton = document.querySelector('.submit');
                    if (submitButton) {
                        submitButton.addEventListener('click', () => {
                            const outputCard = document.querySelector('.output-card');
                            outputCard.classList.add('loading');
                        });
                    }

                    const audioOutputContainer = document.querySelector('.audio-output');
                    if (audioOutputContainer) {
                        const observer = new MutationObserver(() => {
                            const outputCard = document.querySelector('.output-card');
                            if (audioOutputContainer.querySelector('audio') && audioOutputContainer.querySelector('audio').src) {
                                outputCard.classList.remove('loading');
                            }
                        });
                        observer.observe(audioOutputContainer, { childList: true, subtree: true });
                    }
                }, 1000);
            });
        </script>
    """)
    
    gr.Markdown(
        """
        # 🎙️ Voice ChatBot
        ### Berbicara langsung ke mikrofon dan dapatkan jawaban suara dari asisten AI.
        """
    )
    
    with gr.Column():
        with gr.Column(elem_classes="input-card"):
            gr.HTML("""
                <div class="card-header">
                    <div class="card-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ff6f61" stroke-width="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                    </div>
                    <h3 class="card-title">Rekam Pertanyaanmu</h3>
                </div>
            """)
            
            with gr.Column(elem_classes="audio-container"):
                gr.HTML('<div class="waveform"><div class="wave-line"></div></div>')
                audio_input = gr.Audio(
                    sources="microphone",
                    type="numpy",
                    elem_classes="audio-input"
                )
                
                with gr.Row(elem_classes="buttons-container"):
                    submit_btn = gr.Button("Kirim", variant="primary", elem_classes="submit")
                    clear_btn = gr.Button("Hapus", variant="secondary", elem_classes="clear")
            
            with gr.Column(elem_classes="transcript-container"):
                gr.HTML("""
                    <div class="transcript-header">
                        <svg class="transcript-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#ff6f61" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                            <polyline points="10 9 9 9 8 9"></polyline>
                        </svg>
                        <h4 class="transcript-title">Transkrip Input</h4>
                    </div>
                """)
                input_transcript = gr.Markdown("Transkrip tidak tersedia", elem_classes="transcript-content")
        
        with gr.Column(elem_classes="output-card"):
            gr.HTML("""
                <div class="card-header">
                    <div class="card-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#00b7eb" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                        </svg>
                    </div>
                    <h3 class="card-title">Dengar Jawabannya</h3>
                </div>
            """)
            
            with gr.Column(elem_classes="audio-container"):
                gr.HTML('<div class="waveform"><div class="wave-line"></div></div>')
                gr.HTML('<div class="loading-spinner"></div>')
                audio_output = gr.Audio(
                    type="filepath",
                    elem_classes="audio-output"
                )
            
            with gr.Column(elem_classes="transcript-container"):
                gr.HTML("""
                    <div class="transcript-header">
                        <svg class="transcript-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#00b7eb" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                            <polyline points="10 9 9 9 8 9"></polyline>
                        </svg>
                        <h4 class="transcript-title">Transkrip Respons AI</h4>
                    </div>
                """)
                output_transcript = gr.Markdown("Transkrip tidak tersedia", elem_classes="transcript-content")
        
        with gr.Column(elem_classes="log-card"):
            gr.HTML("""
                <div class="card-header">
                    <div class="card-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                            <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path>
                            <path d="M12 16v.01"></path>
                            <path d="M12 13a3 3 0 0 0 3-3V7a3 3 0 1 0-6 0v3a3 3 0 0 0 3 3z"></path>
                        </svg>
                    </div>
                    <h3 class="card-title">Proses Kerja</h3>
                </div>
            """)
            with gr.Column(elem_classes="transcript-container"):
                gr.HTML("""
                    <div class="transcript-header">
                        <svg class="transcript-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                            <polyline points="10 9 9 9 8 9"></polyline>
                        </svg>
                        <h4 class="transcript-title">Log Proses</h4>
                    </div>
                """)
                log_output = gr.Markdown("", elem_classes="log-content")

    loading_state = gr.State(value="")

    submit_btn.click(
        fn=voice_chat,
        inputs=[audio_input, loading_state],
        outputs=[audio_output, input_transcript, output_transcript, log_output, loading_state]
    )

    clear_btn.click(
        fn=clear_inputs,
        inputs=[],
        outputs=[audio_input, audio_output, input_transcript, output_transcript, log_output, loading_state]
    )

demo.launch()