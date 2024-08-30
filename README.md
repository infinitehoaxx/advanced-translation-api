# Advanced Translation API

This is an advanced translation API built with Flask, offering multiple translation services, language detection, caching, and rate limiting.

## Features

- Multiple translation services (Google, Microsoft, Pons)
- Language detection
- URL content translation
- Response caching using Redis
- Rate limiting to prevent abuse
- Comprehensive error handling

## Prerequisites

- Python 3.7+
- Redis server
- .env file with necessary API keys (for Microsoft translator)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/advanced-translation-api.git
   cd advanced-translation-api
   ```

2. Install required packages:
   ```
   pip install flask flask-limiter deep-translator langdetect requests beautifulsoup4 redis python-dotenv
   ```

3. Set up a Redis server (if not already running).

4. Create a `.env` file in the project root and add your Microsoft Translator API key (if you plan to use it):
   ```
   MICROSOFT_TRANSLATOR_KEY=your_api_key_here
   ```

## Usage

1. Start the server:
   ```
   python app.py
   ```

2. The API will be available at `http://localhost:5000`.

## API Endpoints

### 1. Get Supported Languages

- **URL:** `/getLang`
- **Method:** GET
- **Query Parameters:** 
  - `translator` (optional): The translation service to use (default: 'google')
- **Success Response:**
  - Code: 200
  - Content: `{ "en": "English", "fr": "French", ... }`

### 2. Translate Text

- **URL:** `/translate`
- **Method:** POST
- **Data Params:**
  ```json
  {
    "text": "Hello, world!",
    "source_lang": "en",
    "target_lang": "fr",
    "translator": "google"
  }
  ```
- **Success Response:**
  - Code: 200
  - Content: `{ "translated_text": "Bonjour le monde!", "source": "api" }`

### 3. Translate URL Content

- **URL:** `/translate_url`
- **Method:** POST
- **Data Params:**
  ```json
  {
    "url": "https://example.com",
    "source_lang": "auto",
    "target_lang": "es",
    "translator": "google"
  }
  ```
- **Success Response:**
  - Code: 200
  - Content: `{ "translated_text": "..." }`

### 4. Detect Language

- **URL:** `/detect_language`
- **Method:** POST
- **Data Params:**
  ```json
  {
    "text": "Hello, how are you?"
  }
  ```
- **Success Response:**
  - Code: 200
  - Content: `{ "detected_language": "en" }`

## Rate Limiting

- `/getLang`: 10 requests per minute
- `/translate`: 100 requests per minute
- `/translate_url`: 20 requests per minute
- `/detect_language`: 50 requests per minute

## Caching

Translations are cached for 1 hour to improve performance and reduce API calls.

## Error Handling

All endpoints return appropriate error messages and status codes for invalid requests or when services are unavailable.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- [deep_translator](https://github.com/nidhaloff/deep-translator) library
- Flask and its extensions
