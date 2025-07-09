import requests
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

def get_soundcloud_track_info(url):
    """
    Extracts basic info from a SoundCloud URL, ignoring share tracking parameters.
    """
    print(f"Parsing SoundCloud URL: {url}...")
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            # Assuming the structure is soundcloud.com/artist/track-title
            artist = path_parts[-2].replace('-', ' ').title()
            title = path_parts[-1].replace('-', ' ').title()
        else:
            artist = "Unknown Artist"
            title = "Unknown Title"
            
        return {
            "title": title,
            "artist": artist,
        }
    except Exception as e:
        print(f"Could not parse SoundCloud URL: {e}")
        return {
            "title": "Sample Track",
            "artist": "Sample Artist",
        }

def generate_promotional_text(api_key, track_info, user_keywords):
    """
    Generates promotional text using the OpenAI API.
    """
    print("Generating promotional text...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a music promotion expert for an electronic music label.
    Create a short promotional text for the following track. The entire output must be in English.

    Track Information:
    - Title: {track_info['title']}
    - Artist: {track_info['artist']}

    Artist Keywords: {', '.join(user_keywords)}

    The text must contain these three parts, with these exact labels:
    1.  **Hook:** A powerful, one-sentence hook.
    2.  **Body:** A short presentation paragraph (2-3 sentences).
    3.  **Hashtags:** A list of 7 relevant hashtags for social media.

    The tone must be energetic, professional, and cool.
    """
    
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        error_message = f"Error during text generation: {response.text}"
        print(error_message)
        raise Exception(error_message)

def generate_image_url(api_key, track_info, user_keywords, image_style):
    """
    Generates an image via DALL-E 3 and returns the URL.
    """
    print(f"Generating image with style: {image_style}...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Base prompt
    prompt = f"""
    Album cover artwork for an electronic music track.
    Artist: "{track_info['artist']}".
    Track Title: "{track_info['title']}".
    The general mood comes from these keywords: {', '.join(user_keywords)}.

    **Artistic Style: {image_style}.**

    The image must be sophisticated, visually stunning, and modern. It should not contain any text or letters. High resolution, cinematic quality.
    """
    
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        return image_url
    else:
        error_message = f"Error during image generation: {response.text}"
        print(error_message)
        raise Exception(error_message)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.get_json()
        soundcloud_url = data.get('soundcloudUrl')
        user_keywords = data.get('userKeywords')
        api_key = data.get('apiKey')
        # A default style is provided here, but we expect the frontend to send one.
        image_style = data.get('imageStyle', 'Modern and minimalist digital art') 

        if not all([soundcloud_url, user_keywords, api_key]):
            return jsonify({"error": "Missing required fields"}), 400

        # 1. Extract info from URL
        track_info = get_soundcloud_track_info(soundcloud_url)
        
        # 2. Generate promotional text
        promo_text = generate_promotional_text(api_key, track_info, user_keywords)
        
        # 3. Generate image
        image_url = generate_image_url(api_key, track_info, user_keywords, image_style)
        
        return jsonify({
            "promoText": promo_text,
            "imageUrl": image_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server on http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

