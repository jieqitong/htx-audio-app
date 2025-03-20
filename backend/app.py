import os
import sqlite3
import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from typing import List

def get_settings():
    return { "database_path": "transcriptions.db" }

# Whisper model setup
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")

# Database setup
# Ensure the table exists
def init_db(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audio_filename TEXT NOT NULL,
                transcribed_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS transcriptions_v USING FTS5(id, audio_filename, transcribed_text, created_at)
        """)
        conn.commit()

init_db(get_settings()["database_path"])

# To get a database connection and cursor
def get_db_conn_cursor():
    conn = sqlite3.connect(get_settings()["database_path"])
    return conn, conn.cursor()

# FastAPI app instance
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Returns the status of the service
@app.get("/health")
def health_check():
    return {"status": "ok"}

#  Accepts audio files, performs transcription and save results in database
@app.post("/transcribe")
async def transcribe_audio(files: List[UploadFile] = File(...)):
    transcriptions = []

    for file in files:
        if not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Audio files are required.")

        try:
            # Temporary audio file storage
            contents = await file.read()
            temp_file_path = f"temp_{file.filename}"
            with open(temp_file_path, "wb") as f:
                f.write(contents)

            # Performs transcription
            transcription_text = transcriber(temp_file_path)["text"]

            # Save results in database
            conn, cursor = get_db_conn_cursor()
            dt = datetime.datetime.now()
            cursor.execute("INSERT INTO transcriptions (audio_filename, transcribed_text, created_at) VALUES (?, ?, ?)",
                        (file.filename, transcription_text, dt))
            cursor.execute("INSERT INTO transcriptions_v (audio_filename, transcribed_text, created_at) VALUES (?, ?, ?)",
                        (file.filename, transcription_text, dt))
            conn.commit()
            conn.close()

            # Clean up temp file
            os.remove(temp_file_path)
        
            transcriptions.append({"audio_filename": file.filename, "transcribed_text": transcription_text})

        except Exception as e:
            # Clean up temp file, even on error.
            os.remove(temp_file_path)
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    return {"transcriptions": transcriptions}

#  Retrieves all transcriptions from the database
@app.get("/transcriptions")
def get_transcriptions():
    conn, cursor = get_db_conn_cursor()
    cursor.execute("SELECT id, audio_filename, transcribed_text, created_at FROM transcriptions_v")
    transcriptions = [{"audio_filename": row[1], "transcribed_text": row[2], "created_at": row[3]} for row in cursor.fetchall()]
    conn.close()
    return transcriptions

#  Performs a full-text search on transcriptions based on audio file name
@app.get("/search")
def search_transcription(audio_filename: str):
    conn, cursor = get_db_conn_cursor()
    if audio_filename is None or audio_filename == '':
        cursor.execute("SELECT id, audio_filename, transcribed_text, created_at FROM transcriptions_v")
    else:
        cursor.execute("SELECT id, audio_filename, transcribed_text, created_at FROM transcriptions_v WHERE audio_filename MATCH ?", (audio_filename,))
    transcriptions = [{"audio_filename": row[1], "transcribed_text": row[2], "created_at": row[3]} for row in cursor.fetchall()]
    conn.close()
    return transcriptions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)