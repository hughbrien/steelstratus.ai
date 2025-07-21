from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Global variable to store the last request data
last_request_data = {
    'timestamp': None,
    'method': None,
    'url': None,
    'headers': None,
    'data': None
}

def update_last_request():
    """Update the last request data with current request information"""
    global last_request_data
    last_request_data = {
        'timestamp': datetime.now().isoformat(),
        'method': request.method,
        'url': request.url,
        'headers': dict(request.headers),
        'data': request.get_json() if request.is_json else request.get_data(as_text=True)
    }

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook endpoint that accepts both GET and POST requests"""
    update_last_request()
    
    if request.method == 'GET':
        return jsonify({
            'message': 'Webhook GET request received',
            'timestamp': datetime.now().isoformat(),
            'query_params': dict(request.args)
        }), 200
    
    elif request.method == 'POST':
        data = request.get_json() if request.is_json else request.get_data(as_text=True)
        
        # Create the webhook data entry to append to file
        webhook_entry = {
            'timestamp': datetime.now().isoformat(),
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'data': data,
            'remote_addr': request.remote_addr
        }
        
        # Append JSON data to local file
        try:
            with open('webhook_data.json', 'a') as f:
                f.write(json.dumps(webhook_entry) + '\n')
        except Exception as e:
            return jsonify({
                'error': 'Failed to write to file',
                'message': str(e)
            }), 500
        
        return jsonify({
            'message': 'Webhook POST request received and logged',
            'timestamp': datetime.now().isoformat(),
            'received_data': data,
            'logged_to_file': 'webhook_data.json'
        }), 200

@app.route('/lastrequest', methods=['GET'])
def last_request():
    """Return information about the last request received"""
    if last_request_data['timestamp'] is None:
        return jsonify({
            'message': 'No previous requests recorded'
        }), 404
    
    return jsonify(last_request_data), 200

@app.route('/version', methods=['GET'])
def version():
    """Return version information"""
    return jsonify({
        'version': '1.0.0',
        'name': 'Simple REST API Service',
        'python_version': os.sys.version,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/healthz/live')
def health_live():
    """Liveness health check endpoint"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/healthz/ready')
def health_ready():
    """Readiness health check endpoint"""
    return jsonify({
        'status': 'ready'
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)