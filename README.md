# Audio Fraud Detection API

This is a FastAPI application that analyzes audio files for potential fraud based on certain keywords and personal details.

## Setup

1. Install the dependencies using `pip install -r requirements.txt`.
2. Run the server using `uvicorn main:app --reload`.

## Usage

Send a POST request to `http://localhost:8000/analyze-audio/` with an audio file as a form file upload.

