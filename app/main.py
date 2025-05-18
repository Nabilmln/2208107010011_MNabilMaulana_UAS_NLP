from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech
import os
import tempfile
import logging
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("voice-assistant")

app = FastAPI(title="Voice AI Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Voice AI Assistant API is running"}

@app.post("/voice-chat")
async def voice_chat(request: Request, file: UploadFile = File(...)):
    logger.info(f"Received request from {request.client.host} with file: {file.filename}")
    logger.info(f"Request headers: {request.headers}")
    
    # Read uploaded file
    contents = await file.read()
    file_size = len(contents)
    logger.info(f"File received: {file_size} bytes")
    
    if not contents or file_size == 0:
        logger.error("Empty file received")
        return JSONResponse(
            status_code=400,
            content={"error": "Empty file"}
        )
    
    # Speech to text
    logger.info("Starting speech-to-text processing")
    transcript = transcribe_speech_to_text(contents, file_ext=os.path.splitext(file.filename)[1])
    if transcript.startswith("[ERROR]"):
        logger.error(f"STT error: {transcript}")
        return JSONResponse(
            status_code=500,
            content={"error": transcript}
        )
    
    logger.info(f"Transcribed: {transcript}")
    
    # Generate response from LLM
    logger.info("Generating LLM response")
    response_text = generate_response(transcript)
    if response_text.startswith("[ERROR]"):
        logger.error(f"LLM error: {response_text}")
        return JSONResponse(
            status_code=500,
            content={"error": response_text}
        )
    
    logger.info(f"LLM Response: {response_text}")
    
    # Text to speech
    logger.info("Starting text-to-speech processing")
    # Preprocess text to replace problematic characters
    response_text = response_text.replace("'", "").replace('"', '').replace('`', '')
    audio_path = transcribe_text_to_speech(response_text)
    if not audio_path or audio_path.startswith("[ERROR]"):
        logger.error(f"TTS error: {audio_path}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate speech: {audio_path}"}
        )
    
    # Read and encode audio file
    try:
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()
            audio_base64 = base64.b64encode(audio_content).decode("utf-8")
        file_size = len(audio_content)
        logger.info(f"Audio file read: {audio_path} ({file_size} bytes)")
    except Exception as e:
        logger.error(f"Failed to read audio file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to read audio file: {e}"}
        )
    
    # Clean up temporary audio file
    try:
        os.unlink(audio_path)
    except:
        pass
    
    logger.info(f"Sending response with audio and transcripts")
    return JSONResponse(
        status_code=200,
        content={
            "audio_content": audio_base64,
            "input_transcript": transcript,
            "output_transcript": response_text
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)