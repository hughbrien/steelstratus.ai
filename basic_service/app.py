from flask import Flask, request, jsonify
from datetime import datetime, timedelta
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
        'status': 'live'
    }), 200

@app.route('/healthz/ready')
def health_ready():
    """Readiness health check endpoint"""
    return jsonify({
        'status': 'ready'
    }), 200

@app.route('/observer', methods=['GET', 'POST'])
def observer():
    """Observer service: Analyze a REST API service and endpoint based on provided metrics."""
    if request.method == 'GET':
        return jsonify({
            'usage': 'POST JSON metrics to this endpoint. Example payload:',
            'example': {
                'metrics': [
                    {
                        'timestamp': '2024-06-01T12:34:56',
                        'response_time_ms': 1500,
                        'error': False,
                        'compute_density': 0.8
                    },
                    # ... more entries ...
                ]
            }
        }), 200

    # POST: analyze metrics
    data = request.get_json()
    if not data or 'metrics' not in data:
        return jsonify({'error': 'Missing metrics in request body'}), 400

    metrics = data['metrics']
    if not isinstance(metrics, list) or not metrics:
        return jsonify({'error': 'Metrics should be a non-empty list'}), 400

    # Helper to parse timestamp
    def parse_ts(ts):
        return datetime.fromisoformat(ts)

    # Aggregate by timeframes
    from collections import defaultdict
    import math

    timeframes = {
        'hour': lambda dt: dt.replace(minute=0, second=0, microsecond=0),
        'day': lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0),
        'week': lambda dt: dt - timedelta(days=dt.weekday()),
        'month': lambda dt: dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        'year': lambda dt: dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
        'hour_of_day': lambda dt: dt.hour,
        'day_of_week': lambda dt: dt.weekday(),
    }

    # Prepare buckets
    buckets = {k: defaultdict(list) for k in timeframes}

    for entry in metrics:
        try:
            dt = parse_ts(entry['timestamp'])
            for tf, grouper in timeframes.items():
                key = grouper(dt)
                buckets[tf][key].append(entry)
        except Exception:
            continue  # skip malformed entries

    # Scoring function
    def compute_score(entries):
        if not entries:
            return None
        n = len(entries)
        resp_times = [e['response_time_ms'] for e in entries if 'response_time_ms' in e]
        errors = [e for e in entries if e.get('error', False)]
        compute_densities = [e.get('compute_density', 1.0) for e in entries]
        throughput = n
        avg_resp = sum(resp_times) / len(resp_times) if resp_times else 0
        error_rate = len(errors) / n if n else 0
        avg_cd = sum(compute_densities) / len(compute_densities) if compute_densities else 1.0
        # Golden signals: response time, throughput, error rate, compute density
        # Score out of 100
        score = 100
        # Response time penalty
        if avg_resp > 2000:
            score -= min(40, (avg_resp - 2000) / 50)  # up to -40
        # Error rate penalty
        score -= error_rate * 30  # up to -30
        # Compute density penalty (lower is better)
        if avg_cd < 0.5:
            score -= (0.5 - avg_cd) * 20  # up to -10
        # Throughput bonus/penalty
        if throughput > 1000:
            score += 5  # high load bonus
        elif throughput < 100:
            score -= 10  # low load penalty
        # Clamp
        score = max(1, min(100, int(round(score))))
        return {
            'score': score,
            'avg_response_time_ms': avg_resp,
            'throughput': throughput,
            'error_rate': error_rate,
            'avg_compute_density': avg_cd
        }

    result = {}
    for tf, groups in buckets.items():
        tf_scores = {}
        for key, entries in groups.items():
            tf_scores[str(key)] = compute_score(entries)
        result[tf] = tf_scores

    return jsonify({'analysis': result}), 200

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

# Basic Service: Example REST API with webhook and health endpoints
# Run with: python app.py
if __name__ == '__main__':
    print('Starting Basic Service on port 5001...')
    app.run(host='0.0.0.0', port=5000, debug=True)
