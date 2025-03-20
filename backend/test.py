import os
import pytest
from app import app, init_db
from fastapi.testclient import TestClient
from unittest.mock import patch

client = TestClient(app)
settings = { "database_path": "test_transcriptions.db" }

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db(settings["database_path"])
    yield
    os.remove(settings["database_path"])

def test_transcribe_invalid_file_type():
    files = [("files", ("random text.txt", open("./test_file/random text.txt", "rb"), "text/plain"))]
    response = client.post("/transcribe", files=files)
    assert response.json()["detail"] == "Invalid file type. Audio files are required."

@patch("app.get_settings")
def test_transcribe(get_settings):
    get_settings.return_value = settings

    files = [("files", ("Random.mp3", open("./test_file/Random.mp3", "rb"), "audio/mp3")),
             ("files", ("Sample 2.mp3", open("./test_file/Sample 2.mp3", "rb"), "audio/mp3"))]
    response = client.post("/transcribe", files=files)

    assert response.status_code == 200
    assert "transcriptions" in response.json()
    assert len(response.json()["transcriptions"]) == 2
    for i in range(2):
        assert "transcribed_text" in response.json()["transcriptions"][i]
        assert response.json()["transcriptions"][i]["audio_filename"] == files[i][1][0]

@patch("app.get_settings")
def test_search(get_settings):
    get_settings.return_value = settings

    response = client.get("/search?audio_filename=sample")
    assert response.status_code == 200
    assert len(response.json()) == 1


