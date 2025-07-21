# steelstratus.ai
steelstratus.ai - Steel Stratus Observability Platform

## Project Overview
- Steel Stratus Observability Index / ApDex
- Creates a solution that generates scores between 1 and 100 for REST API services
- Scoring based on Golden Signals: Response Time, Throughput, Error Rate and Compute Density
- Computes scores every hour, day, week, month, year
- Includes options for Hour of the Day and Day of the Week analysis

## REST API Service

### Installation
```bash
pip install -r requirements.txt
```

### Running the Service
```bash
python app.py
```
The service will start on `http://localhost:5000`

### API Endpoints

#### 1. Webhook Endpoint
- **URL**: `/webhook`
- **Methods**: `GET`, `POST`
- **Description**: 
  - GET: Returns webhook status and query parameters
  - POST: Accepts JSON data and appends it to `webhook_data.json` file
- **Response**: JSON with request details

#### 2. Last Request
- **URL**: `/lastrequest`
- **Method**: `GET`
- **Description**: Returns information about the last request received
- **Response**: JSON with timestamp, method, URL, headers, and data

#### 3. Version Information
- **URL**: `/version`
- **Method**: `GET`
- **Description**: Returns service version and system information
- **Response**: JSON with version, name, Python version, and timestamp

#### 4. Health Check - Liveness
- **URL**: `/healthz/live`
- **Method**: `GET`
- **Description**: Liveness probe for container orchestration
- **Response**: `{"status":"live"}`

#### 5. Health Check - Readiness
- **URL**: `/healthz/ready`
- **Method**: `GET`
- **Description**: Readiness probe for container orchestration
- **Response**: `{"status":"ready"}`

### Example Usage

#### Send data to webhook:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "test data", "value": 123}'
```

#### Check service health:
```bash
curl http://localhost:5000/healthz/live
curl http://localhost:5000/healthz/ready
```

#### Get version info:
```bash
curl http://localhost:5000/version
```

### Data Storage
- Webhook POST requests are logged to `webhook_data.json`
- Each entry contains timestamp, method, URL, headers, data, and client IP
- Data is appended (not overwritten) to maintain complete history

## Future Development
This REST API serves as the foundation for the Steel Stratus observability platform. Future iterations will include:
- Golden Signals monitoring implementation
- Scoring algorithms (1-100 scale)
- Time-based analysis and reporting
- Performance metrics collection and analysis 

