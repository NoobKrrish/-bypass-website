from flask import Flask, request, jsonify
import requests
import re
import base64
from urllib.parse import urlparse, unquote

app = Flask(__name__)

class URLBypasser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def bypass_url(self, url):
        try:
            print(f"Bypassing: {url}")
            
            response = self.session.get(url, allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302, 303]:
                redirect_url = response.headers.get('Location', '')
                if redirect_url and self.is_valid_url(redirect_url):
                    return redirect_url
            
            final_url = self.extract_from_html(url, response.text)
            if final_url != url:
                return final_url
                
            param_url = self.extract_from_params(url)
            if param_url != url:
                return param_url
                
            return url
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_from_html(self, url, html):
        patterns = [
            (r'window\.location\s*=\s*["\']([^"\']+)["\']', None),
            (r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', None),
            (r'window\.open\s*\(\s*["\']([^"\']+)["\']', None),
            (r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*url=([^"\']+)', None),
            (r'atob\s*\(\s*["\']([^"\']+)["\']', self.decode_base64_url),
            (r'[\?&](?:url|u|link|target|redirect)=([^&"\']+)', None),
        ]
        
        for pattern, processor in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if processor:
                    result = processor(match)
                else:
                    result = match
                
                if self.is_valid_url(result):
                    return result
                   
        return url
    
    def extract_from_params(self, url):
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            for key in ['url', 'u', 'link', 'target', 'redirect']:
                if key in params:
                    value = params[key][0]
                    decoded = unquote(value)
                    if self.is_valid_url(decoded):
                        return decoded
            
            if 'r' in params:
                try:
                    decoded = base64.b64decode(params['r'][0]).decode('utf-8')
                    if self.is_valid_url(decoded):
                        return decoded
                except:
                    pass
                    
        except Exception:
            pass
            
        return url
    
    def decode_base64_url(self, encoded_str):
        try:
            decoded = base64.b64decode(encoded_str).decode('utf-8')
            return decoded
        except:
            return encoded_str
    
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
            return jsonify({
                "success": False, 
                "message": "URL parameter is required"
            })
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = bypasser.bypass_url(url)
        
        return jsonify({
            "success": True,
            "original_url": url,
            "bypassed_url": result,
            "message": "Bypass completed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Server error: {str(e)}"
        })

if __name__ == '__main__':
    app.run(debug=True)
