from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from deep_translator import GoogleTranslator, MicrosoftTranslator, PonsTranslator
from langdetect import detect
import requests
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv
from functools import lru_cache
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

# Setup rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

SUPPORTED_TRANSLATORS = {
    'google': GoogleTranslator,
    'microsoft': MicrosoftTranslator,
    'pons': PonsTranslator
}

# Simple in-memory cache
cache = {}

def get_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()

@lru_cache(maxsize=128)
def get_supported_languages(translator):
    return SUPPORTED_TRANSLATORS[translator]().get_supported_languages(as_dict=True)

@app.route('/getLang', methods=['GET'])
@limiter.limit("10/minute")
def get_lang():
    translator = request.args.get('translator', 'google')
    if translator not in SUPPORTED_TRANSLATORS:
        return jsonify({"error": "Unsupported translator"}), 400
    
    languages = get_supported_languages(translator)
    return jsonify(languages)

@app.route('/translate', methods=['POST'])
@limiter.limit("100/minute")
def translate():
    data = request.json
    text = data.get('text')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang')
    translator = data.get('translator', 'google')
    
    if not text or not target_lang:
        return jsonify({"error": "Missing text or target language"}), 400
    
    if translator not in SUPPORTED_TRANSLATORS:
        return jsonify({"error": "Unsupported translator"}), 400
    
    cache_key = f"{translator}:{source_lang}:{target_lang}:{text}"
    current_time = datetime.now()
    
    if cache_key in cache:
        cached_result, timestamp = cache[cache_key]
        if current_time - timestamp < timedelta(hours=1):
            return jsonify({"translated_text": cached_result, "source": "cache"})
    
    try:
        if source_lang == 'auto':
            translated = SUPPORTED_TRANSLATORS[translator](target=target_lang).translate(text)
        else:
            translated = SUPPORTED_TRANSLATORS[translator](source=source_lang, target=target_lang).translate(text)
        
        cache[cache_key] = (translated, current_time)
        return jsonify({"translated_text": translated, "source": "api"})
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 400

@app.route('/translate_url', methods=['POST'])
@limiter.limit("20/minute")
def translate_url():
    data = request.json
    url = data.get('url')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang')
    translator = data.get('translator', 'google')
    
    if not url or not target_lang:
        return jsonify({"error": "Missing URL or target language"}), 400
    
    if translator not in SUPPORTED_TRANSLATORS:
        return jsonify({"error": "Unsupported translator"}), 400
    
    try:
        text = get_text_from_url(url)
        if source_lang == 'auto':
            translated = SUPPORTED_TRANSLATORS[translator](target=target_lang).translate(text)
        else:
            translated = SUPPORTED_TRANSLATORS[translator](source=source_lang, target=target_lang).translate(text)
        return jsonify({"translated_text": translated})
    except Exception as e:
        return jsonify({"error": f"URL translation failed: {str(e)}"}), 400

@app.route('/detect_language', methods=['POST'])
@limiter.limit("50/minute")
def detect_language():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "Missing text"}), 400
    
    try:
        detected_lang = detect(text)
        return jsonify({"detected_language": detected_lang})
    except Exception as e:
        return jsonify({"error": f"Language detection failed: {str(e)}"}), 400

# This is needed for PythonAnywhere
application = app
