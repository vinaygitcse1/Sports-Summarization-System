from flask import Flask
from functools import wraps
import secrets

def setup_security_headers(app: Flask):
    """Add security headers to all responses"""
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # CSP Header
        response.headers['Content-Security-Policy'] = \
            "default-src 'self'; " \
            "script-src 'self' https://cdn.jsdelivr.net https://code.jquery.com; " \
            "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com 'unsafe-inline'; " \
            "font-src 'self' https://cdnjs.cloudflare.com; " \
            "img-src 'self' data: https:;"
        
        return response
    
    return app

def generate_csrf_token():
    return secrets.token_hex(32)

def validate_file_type(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions