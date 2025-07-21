from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
import math

app = Flask(__name__)

# Observer Service: Analyzes REST API metrics and computes health scores by time period
# Run with: python observer_service.py
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

    timeframes = {
        'hour': lambda dt: dt.replace(minute=0, second=0, microsecond=0),
        'day': lambda dt: dt.replace(hour=0, minute=0, second=0, microsecond=0),
        'week': lambda dt: dt - timedelta(days=dt.weekday()),
        'month': lambda dt: dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        'year': lambda dt: dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
        'hour_of_day': lambda dt: dt.hour,
        'day_of_week': lambda dt: dt.weekday(),
    }

    buckets = {k: defaultdict(list) for k in timeframes}

    for entry in metrics:
        try:
            dt = parse_ts(entry['timestamp'])
            for tf, grouper in timeframes.items():
                key = grouper(dt)
                buckets[tf][key].append(entry)
        except Exception:
            continue  # skip malformed entries

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
        score = 100
        if avg_resp > 2000:
            score -= min(40, (avg_resp - 2000) / 50)
        score -= error_rate * 30
        if avg_cd < 0.5:
            score -= (0.5 - avg_cd) * 20
        if throughput > 1000:
            score += 5
        elif throughput < 100:
            score -= 10
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

if __name__ == '__main__':
    print('Starting Observer Service on port 5001...')
    app.run(host='0.0.0.0', port=5001, debug=True) 