# URL to NanoGPT Image Generator

A simple Flask application that converts URL requests into NanoGPT API calls for image generation.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your NanoGPT API key:
```bash
export NANOGPT_API_KEY="your_api_key_here"
```

3. Run the application:
```bash
python app.py
```

## Usage

### Web Interface
Navigate to `http://localhost:5000` and enter your prompt in the form.

### Direct URL Access
Use the standard query parameter format:
```
http://localhost:5000/generate?prompt=a+beautiful+sunset+over+mountains
```

## Features

- Simple URL query structure using standard `?prompt=` parameter
- Clean web interface with embedded image display
- Error handling for missing prompts or API failures
- Download option for generated images