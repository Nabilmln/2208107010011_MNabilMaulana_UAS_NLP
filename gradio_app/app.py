import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
import base64

def voice_chat(audio):
    if audio is None:
        return None, "", "No audio input provided"
    
    sr, audio_data = audio

    # Save as .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        scipy.io.wavfile.write(tmpfile.name, sr, audio_data)
        audio_path = tmpfile.name

    # Send to FastAPI endpoint
    with open(audio_path, "rb") as f:
        files = {"file": ("voice.wav", f, "audio/wav")}
        response = requests.post("http://localhost:8000/voice-chat", files=files)

    # Clean up temporary file
    try:
        os.unlink(audio_path)
    except:
        pass

    if response.status_code == 200:
        data = response.json()
        # Save audio response
        output_audio_path = os.path.join(tempfile.gettempdir(), "tts_output.wav")
        with open(output_audio_path, "wb") as f:
            f.write(base64.b64decode(data["audio_content"]))
        
        # Format chat history
        chat_history = [
            ("You", data["input_transcript"]),
            ("Assistant", data["output_transcript"])
        ]
        logs = "Logs not available (backend does not provide logs)"
        chat_display = update_chat_display(chat_history)
        return output_audio_path, chat_display, logs
    else:
        return None, "", f"Error: {response.status_code} - {response.text}"

def update_chat_display(history):
    if not history:
        return "<div class='chat-container'>No messages yet</div>"
    html = '<div class="chat-container">'
    for sender, message in history:
        class_name = "user" if sender == "You" else "assistant"
        html += f'<div class="chat-message {class_name}">{message}</div>'
    html += '</div>'
    return html

# Custom CSS for WhatsApp-like theme
whatsapp_css = """
/* General layout */
body {
    background-color: #f0f2f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* Header */
h1 {
    background-color: #00a884;
    color: white;
    padding: 10px;
    margin: -10px -10px 20px -10px;
    border-radius: 8px 8px 0 0;
}

/* Chat container */
.chat-container {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 10px;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 20px;
}

/* Chat messages */
.chat-message {
    margin: 5px 10px;
    padding: 8px 12px;
    border-radius: 8px;
    max-width: 70%;
    word-wrap: break-word;
}

.chat-message.user {
    background-color: #d9fdd3;
    margin-left: auto;
    text-align: right;
}

.chat-message.assistant {
    background-color: #f0f2f5;
    margin-right: auto;
    text-align: left;
}

/* Log section */
.log-container {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 10px;
    max-height: 200px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 12px;
    color: #333;
}

/* Button */
button {
    background-color: #00a884 !important;
    color: white !important;
    border-radius: 8px !important;
}

button:hover {
    background-color: #008c6e !important;
}

/* Audio input/output */
audio {
    width: 100%;
    border-radius: 8px;
}
"""

# UI Gradio
with gr.Blocks(css=whatsapp_css) as demo:
    gr.Markdown("# 🎙 Voice Chatbot")
    gr.Markdown("Berbicara langsung ke mikrofon dan dapatkan jawaban suara dari asisten AI.")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources="microphone", type="numpy", label="🎤 Rekam Pertanyaan Anda")
            submit_btn = gr.Button("🔁 Submit")
        with gr.Column():
            audio_output = gr.Audio(type="filepath", label="🔊 Balasan dari Asisten")

    chat_display = gr.HTML(label="Chat History", value="<div class='chat-container'>No messages yet</div>")
    
    with gr.Accordion("Show Logs", open=False):
        log_display = gr.Textbox(value="", label="Processing Logs", lines=10, max_lines=20, elem_classes="log-container")

    submit_btn.click(
        fn=voice_chat,
        inputs=audio_input,
        outputs=[audio_output, chat_display, log_display]
    )

demo.launch()