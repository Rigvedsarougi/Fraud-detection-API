import os
import re
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File
from pydub import AudioSegment
import speech_recognition as sr
import pandas as pd

app = FastAPI()

def analyze_text_for_personal_details(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    phone_pattern = re.compile(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b')
    emails_found = re.findall(email_pattern, text)
    phones_found = re.findall(phone_pattern, text)
    return emails_found, phones_found

def detect_keywords(input_text):
    keywords = [
        'Job guarantee',
        '100% placement guarantee',
        'Personal account',
        'Refund',
        'S4 Hana',
        'Server Access',
        'Free classes',
        'Lifetime Membership',
        'Providing classes in token amount',
        'Pay later',
        'Global',
        'Abusive words',
        'Sarcastic',
        'Rude',
        'Darling in ILX',
        'Freelancing support we are provided',
        'Placement support we are provided',
        'Affirm',
        'Free classes we are not provided'
    ]

    keyword_presence = {keyword: bool(re.search(re.escape(keyword), input_text, re.IGNORECASE)) for keyword in keywords}

    return keyword_presence

def process_single_audio_file(audio_file) -> Dict:
    results = []
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_mp3(audio_file.file)
    chunk_size_ms = 5000
    chunks = [audio[i:i + chunk_size_ms] for i in range(0, len(audio), chunk_size_ms)]
    transcription = ""
    for i, chunk in enumerate(chunks):
        chunk.export("temp.wav", format="wav")
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                transcription += text + " "
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                pass
    emails, phones = analyze_text_for_personal_details(transcription)
    keyword_results = detect_keywords(transcription)
    result = {
        'File Name': audio_file.filename,
        'Fraud Detection': 'Fraud detected' if any(keyword_results.values()) else 'Not fraud detected',
        **keyword_results,
        'Personal Details': {'Emails': emails, 'Phones': phones}
    }
    results.append(result)
    os.remove("temp.wav")
    return result

@app.post("/analyze-audio/")
async def analyze_audio(audio_file: UploadFile = File(...)):
    result = process_single_audio_file(audio_file)
    return result
