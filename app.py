from flask import Flask, render_template, request, jsonify, send_file, make_response
import requests
import json
import os
from urllib.parse import unquote
import base64
from datetime import datetime, timedelta
import hashlib
from io import BytesIO

app = Flask(__name__)

BASE_URL = "https://nano-gpt.com/api"
API_KEY = os.getenv('NANOGPT_API_KEY')

# In-memory cache for storing generated images
image_cache = {} 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    prompt = request.args.get('prompt', '')
    
    if not prompt:
        return render_template('error.html', error="No prompt provided"), 400
    
    prompt = unquote(prompt)
    
    try:
        # Check if we need to return just the image (for embedding)
        if request.args.get('embed') == 'true' or request.headers.get('Accept', '').startswith('image/'):
            image_data = get_or_generate_image(prompt)
            img_io = BytesIO(base64.b64decode(image_data))
            img_io.seek(0)
            response = make_response(send_file(img_io, mimetype='image/png'))
            response.headers['Cache-Control'] = 'public, max-age=14400'  # 4 hours
            return response
        else:
            # Return the HTML page
            image_url = get_or_generate_image(prompt)
            return render_template('result.html', prompt=prompt, image_url=image_url)
    except Exception as e:
        return render_template('error.html', error=str(e)), 500

def get_cache_key(prompt):
    """Generate a unique cache key for the prompt"""
    return hashlib.md5(prompt.encode()).hexdigest()

def is_cache_valid(cache_entry):
    """Check if cache entry is still valid (within 4 hours)"""
    if not cache_entry:
        return False
    return datetime.now() < cache_entry['expiry']

def get_or_generate_image(prompt):
    """Get image from cache or generate new one"""
    cache_key = get_cache_key(prompt)
    
    # Check cache
    if cache_key in image_cache:
        cache_entry = image_cache[cache_key]
        if is_cache_valid(cache_entry):
            return cache_entry['image_data']
    
    # Generate new image
    image_data = generate_image(prompt)
    
    # Store in cache with expiry time
    image_cache[cache_key] = {
        'image_data': image_data,
        'expiry': datetime.now() + timedelta(hours=4),
        'prompt': prompt
    }
    
    return image_data

def generate_image(prompt):
    headers = {
        "x-api-key": f"{API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "hidream",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    response = requests.post(
        f"{BASE_URL}/generate-image",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result['data'][0]['b64_json']

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
