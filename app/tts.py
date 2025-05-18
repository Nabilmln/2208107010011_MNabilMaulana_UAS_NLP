import os
import uuid
import tempfile
import subprocess
import wave

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COQUI_DIR = os.path.join(BASE_DIR, "coqui_utils")
COQUI_MODEL_PATH = os.path.join(COQUI_DIR, "checkpoint_1260000-inference.pth")
COQUI_CONFIG_PATH = os.path.join(COQUI_DIR, "config.json")
COQUI_SPEAKER = "ardi"

def transcribe_text_to_speech(text: str) -> str:
    """
    Convert text to speech using Coqui TTS.
    Args:
        text (str): Text to convert to speech.
    Returns:
        str: Path to the generated audio file or error message.
    """
    output_dir = os.path.join(tempfile.gettempdir(), "voice_assistant_tts")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"tts_{uuid.uuid4()}.wav")

    # Preprocess text to remove problematic characters
    text = text.encode('ascii', errors='ignore').decode('ascii').strip()
    if not text:
        print(f"[ERROR] Empty text after preprocessing")
        return "[ERROR] Empty text after preprocessing"

    cmd = [
        "tts",
        "--text", text,
        "--model_path", COQUI_MODEL_PATH,
        "--config_path", COQUI_CONFIG_PATH,
        "--speaker_idx", COQUI_SPEAKER,
        "--out_path", output_path
    ]
    
    try:
        print(f"[INFO] Running TTS command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[INFO] TTS stdout: {result.stdout}")
        
        # Validate WAV file
        if not os.path.exists(output_path):
            print(f"[ERROR] TTS output file not created: {output_path}")
            return "[ERROR] TTS failed to create output file"
            
        if os.path.getsize(output_path) == 0:
            print(f"[ERROR] TTS output file is empty: {output_path}")
            return "[ERROR] TTS created empty file"
            
        with wave.open(output_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            framerate = wav_file.getframerate()
            frames = wav_file.getnframes()
            print(f"[INFO] Valid WAV: {channels} ch, {framerate} Hz, {frames} frames")
            
            if frames < 100:
                print(f"[WARNING] WAV file has very few frames: {frames}")
                return "[ERROR] TTS generated insufficient audio"
                
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] TTS subprocess failed: {e}")
        print(f"[ERROR] TTS stderr: {e.stderr}")
        return "[ERROR] Failed to synthesize speech"
    except wave.Error as e:
        print(f"[ERROR] Invalid WAV file generated: {e}")
        return "[ERROR] Invalid WAV file"
    except FileNotFoundError as e:
        print(f"[ERROR] File not found during TTS: {e}")
        return "[ERROR] File not found"
    except Exception as e:
        print(f"[ERROR] Unexpected error in TTS: {str(e)}")
        return f"[ERROR] {str(e)}"

    print(f"[INFO] Output audio saved to: {output_path}")
    return output_path