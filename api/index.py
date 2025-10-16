from flask import Flask, request, jsonify
import requests
import re
import base64
from urllib.parse import urlparse, unquote
import os

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

class URLBypasser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def bypass_url(self, url):
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302, 303]:
                redirect_url = response.headers.get('Location', '')
                if redirect_url and self.is_valid_url(redirect_url):
                    return redirect_url
            
            final_url = self.extract_from_html(response.text)
            if final_url and final_url != url:
                return final_url
                
            return url
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_from_html(self, html):
        patterns = [
            r'window\.location\s*=\s*["\']([^"\']+)["\']',
            r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
            r'window\.open\s*\(\s*["\']([^"\']+)["\']',
            r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*url=([^"\']+)',
            r'atob\s*\(\s*["\']([^"\']+)["\']',
            r'[\?&](?:url|u|link|target|redirect)=([^&"\']+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match
                if 'atob' in pattern:
                    try:
                        url = base64.b64decode(match).decode('utf-8')
                    except:
                        pass
                
                if self.is_valid_url(url):
                    return url
        return None
    
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False

bypasser = URLBypasser()

@app.route('/')
def home():
    return "URL Bypasser API - Made by @GhostKiller777"

@app.route('/api/bypass', methods=['POST', 'GET'])
def api_bypass():
    try:
        if request.method == 'POST':
            data = request.get_json()
            url = data.get('url', '').strip()
        else:
            url = request.args.get('url', '').strip()
        
        if not url:
            return jsonify({"success": False, "message": "URL is required"})
        
        result = bypasser.bypass_url(url)
        
        return jsonify({
            "success": True,
            "original_url": url,
            "bypassed_url": result,
            "message": "Bypass completed successfully"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
