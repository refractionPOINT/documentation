# Extension Developer Troubleshooting Guide

This document provides comprehensive guidance for testing, deploying, and debugging LimaCharlie extensions.

## Table of Contents

- [Testing Strategies](#testing-strategies)
- [Local Development](#local-development)
- [Deployment Guide](#deployment-guide)
- [Common Issues](#common-issues)
- [Debugging Techniques](#debugging-techniques)
- [Performance Optimization](#performance-optimization)

## Testing Strategies

### Local Testing

#### 1. Set Up Local HTTPS Server

**Golang**:
```bash
# Run with environment variables
export SHARED_SECRET="your-32-char-secret-here"
go run main.go --port 8080
```

**Python**:
```bash
# Run with environment variables
export SHARED_SECRET="your-32-char-secret-here"
python extension.py --port 8080
```

#### 2. Use ngrok for Webhook Testing

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start ngrok tunnel
ngrok http 8080

# Output:
# Forwarding https://abc123.ngrok.io -> http://localhost:8080

# Use https://abc123.ngrok.io as your extension Destination URL
```

**Benefits**:
- Test locally without deploying
- Inspect webhook payloads in ngrok dashboard
- Debug signature verification
- See request/response timing

#### 3. Test Webhook Signatures

```go
package main

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
    "log"
)

func verifySignature(body []byte, signature string, secret string) bool {
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write(body)
    expected := hex.EncodeToString(mac.Sum(nil))

    log.Printf("Received signature: %s", signature)
    log.Printf("Expected signature: %s", expected)

    return hmac.Equal([]byte(expected), []byte(signature))
}

// Use in your webhook handler:
func webhookHandler(w http.ResponseWriter, r *http.Request) {
    body, _ := ioutil.ReadAll(r.Body)
    signature := r.Header.Get("X-LC-Signature")

    if !verifySignature(body, signature, os.Getenv("SHARED_SECRET")) {
        http.Error(w, "Invalid signature", http.StatusForbidden)
        return
    }

    // Process webhook...
}
```

### Testing Configuration Validation

#### Via CLI

```bash
# Update configuration to trigger validation
limacharlie hive set extension_configuration my-ext '{
  "api_key": "test123",
  "timeout": 60
}'

# Check for validation errors
limacharlie hive get extension_configuration my-ext
```

#### Via Web UI

1. Navigate to extension page
2. Edit configuration in UI
3. Save and observe validation feedback
4. Check browser console for errors

#### Test Invalid Configurations

```bash
# Test missing required field
limacharlie hive set extension_configuration my-ext '{
  "timeout": 60
}'
# Should return validation error

# Test invalid value
limacharlie hive set extension_configuration my-ext '{
  "api_key": "test",
  "timeout": 999999
}'
# Should return validation error if you have max filter
```

### Testing Requests

#### Via CLI

```bash
# Test basic request
limacharlie extension request \
  --name my-scanner \
  --action scan \
  --data '{"sid": "sensor-id-here"}'

# Test with complex parameters
limacharlie extension request \
  --name my-scanner \
  --action scan \
  --data '{
    "targets": [
      {"sid": "sensor-1", "path": "/usr/bin", "depth": 3},
      {"sid": "sensor-2", "path": "/tmp", "depth": 5}
    ]
  }'
```

#### Via API

```bash
# Using curl
curl -X POST "https://api.limacharlie.io/v1/ext/my-scanner/request" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "oid": "your-org-id",
    "action": "scan",
    "params": {
      "sid": "sensor-id"
    }
  }'

# Save response to file for inspection
curl -X POST "https://api.limacharlie.io/v1/ext/my-scanner/request" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"oid": "org-id", "action": "scan", "params": {"sid": "sid"}}' \
  -o response.json
```

#### Via D&R Rules

Create a test D&R rule:

```yaml
detect:
  event: NEW_PROCESS
  op: is
  path: event/FILE_PATH
  value: /usr/bin/test-trigger
respond:
  - action: extension request
    extension name: my-scanner
    extension action: scan
    extension request:
      sid: '{{ .routing.sid }}'
```

Test by triggering the detection:
```bash
# On the sensor, run:
/usr/bin/test-trigger
```

### Testing Events

#### Subscribe Event

```bash
# Subscribe a test organization
limacharlie extension subscribe --name my-ext --oid test-org-id

# Check extension logs for subscribe event handling
```

#### Unsubscribe Event

```bash
# Unsubscribe organization
limacharlie extension unsubscribe --name my-ext --oid test-org-id

# Verify cleanup in extension logs
```

#### Update Event

The update event fires daily. To test:

```bash
# Manually trigger update event via API
curl -X POST "https://your-extension.com/webhook" \
  -H "Content-Type: application/json" \
  -H "X-LC-Signature: $(echo -n '{"event":"update","oid":"test-org"}' | openssl dgst -sha256 -hmac 'your-secret' | cut -d' ' -f2)" \
  -d '{"event":"update","oid":"test-org"}'
```

## Local Development

### Development Environment Setup

#### Golang

```bash
# Create project
mkdir my-extension
cd my-extension
go mod init my-extension

# Install dependencies
go get github.com/refractionPOINT/lc-extension

# Create main.go
# ... your extension code ...

# Run locally
export SHARED_SECRET="test-secret-32-characters-long"
go run main.go
```

#### Python

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install limacharlie

# Create extension.py
# ... your extension code ...

# Run locally
export SHARED_SECRET="test-secret-32-characters-long"
python extension.py
```

### Hot Reloading

#### Using air (Golang)

```bash
# Install air
go install github.com/cosmtrek/air@latest

# Create .air.toml
cat > .air.toml << EOF
root = "."
tmp_dir = "tmp"

[build]
  cmd = "go build -o ./tmp/main ."
  bin = "tmp/main"
  include_ext = ["go"]
  exclude_dir = ["tmp"]
EOF

# Run with hot reload
air
```

#### Using nodemon (Python)

```bash
# Install nodemon
npm install -g nodemon

# Run with hot reload
nodemon --exec python extension.py
```

### Mock Testing

Create mock SDK for unit testing:

```go
package main

import (
    "testing"
)

type MockSDK struct {
    HiveData map[string]interface{}
}

func (m *MockSDK) Hive() *MockHive {
    return &MockHive{data: m.HiveData}
}

type MockHive struct {
    data map[string]interface{}
}

func (h *MockHive) Get(namespace, key string) (map[string]interface{}, error) {
    return h.data, nil
}

func TestScanAction(t *testing.T) {
    mockSDK := &MockSDK{
        HiveData: map[string]interface{}{
            "timeout": 60,
        },
    }

    ctx := &Context{
        SDK: mockSDK,
        Params: map[string]interface{}{
            "sid": "test-sensor-id",
        },
    }

    result, err := handleScan(ctx)
    if err != nil {
        t.Fatalf("handleScan failed: %v", err)
    }

    // Assert result
    if result["status"] != "completed" {
        t.Errorf("Expected status 'completed', got %v", result["status"])
    }
}
```

## Deployment Guide

### Google Cloud Run

#### 1. Create Dockerfile

```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o extension

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/extension .

EXPOSE 8080
CMD ["./extension"]
```

#### 2. Build and Push

```bash
# Set project ID
export PROJECT_ID=your-gcp-project
export IMAGE_NAME=my-extension

# Build
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME .

# Configure Docker for GCR
gcloud auth configure-docker

# Push
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME
```

#### 3. Deploy

```bash
# Deploy to Cloud Run
gcloud run deploy $IMAGE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SHARED_SECRET=your-secret-here \
  --max-instances 10 \
  --memory 512Mi

# Get service URL
gcloud run services describe $IMAGE_NAME \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

#### 4. Update Extension

Use the URL from Cloud Run as your extension's Destination URL.

### AWS Lambda

#### 1. Create Lambda Handler

**Python**:
```python
import json
import os
from lambda_handler import process_extension_request

def lambda_handler(event, context):
    # Extract webhook data
    body = json.loads(event['body'])
    signature = event['headers'].get('x-lc-signature', '')

    # Verify signature
    if not verify_signature(event['body'], signature):
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Invalid signature'})
        }

    # Process request
    try:
        response = process_extension_request(body)
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def verify_signature(body, signature):
    import hmac
    import hashlib

    secret = os.environ['SHARED_SECRET']
    expected = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

#### 2. Package and Deploy

```bash
# Install dependencies
pip install -t package/ limacharlie

# Add your code
cp lambda_handler.py package/

# Create deployment package
cd package
zip -r ../lambda.zip .
cd ..
zip -g lambda.zip lambda_handler.py

# Deploy
aws lambda create-function \
  --function-name my-extension \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda.zip \
  --environment Variables="{SHARED_SECRET=your-secret}"

# Create API Gateway
aws apigatewayv2 create-api \
  --name my-extension-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:REGION:ACCOUNT:function:my-extension
```

### Custom Infrastructure

#### Using Docker Compose

```yaml
version: '3.8'

services:
  extension:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SHARED_SECRET=${SHARED_SECRET}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - extension
```

**nginx.conf**:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream extension {
        server extension:8080;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://extension;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Common Issues

### Extension Not Receiving Webhooks

#### Issue: No webhooks arriving

**Diagnosis**:
```bash
# Test URL accessibility
curl -X POST https://your-extension.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Solutions**:
1. Verify URL is publicly accessible (not localhost)
2. Check firewall rules allow incoming HTTPS
3. Ensure HTTPS (not HTTP) is configured
4. Verify no authentication required on webhook endpoint
5. Check extension definition has correct URL

#### Issue: Webhooks arriving but failing

**Diagnosis**:
```bash
# Check extension logs
# Cloud Run:
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=my-extension" --limit 50

# Lambda:
aws logs tail /aws/lambda/my-extension --follow

# Docker:
docker logs -f container-name
```

**Solutions**:
1. Verify signature verification logic
2. Check shared secret matches extension definition
3. Ensure JSON parsing handles all field types
4. Validate environment variables are set

### Schema Not Updating in UI

#### Issue: Changes to schema not visible

**Solutions**:
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check schema JSON syntax with validator:
   ```bash
   cat schema.json | jq .
   ```
4. Verify schema via API:
   ```bash
   limacharlie extension get-schema --name my-ext
   ```
5. Check for schema validation errors in extension logs

### Configuration Validation Failing

#### Issue: Cannot save configuration

**Diagnosis**:
```go
// Add detailed logging to validation
func validateConfig(config map[string]interface{}) error {
    log.Printf("Validating config: %+v", config)

    for key, value := range config {
        log.Printf("Field %s: type=%T, value=%v", key, value, value)
    }

    // Your validation logic

    return nil
}
```

**Solutions**:
1. Check all required fields are present
2. Verify data types match schema (JSON numbers are float64 in Go)
3. Ensure nested objects/arrays handled correctly
4. Test with minimal valid configuration first

### SDK Permissions Errors

#### Issue: SDK operations fail with permission errors

**Diagnosis**:
```go
sensor, err := ctx.SDK.Sensor(sid).Get()
if err != nil {
    log.Printf("Permission error: %v", err)
    // Error: missing sensor.get permission
}
```

**Solutions**:
1. Check extension definition includes required permission
2. Update extension permissions:
   ```json
   "permissions": [
     "sensor.get",
     "sensor.task",
     "dr.get",
     "dr.set"
   ]
   ```
3. Test with minimal permissions first
4. Refer to REFERENCE.md for permission names

### Request Parameter Issues

#### Issue: Parameters not arriving as expected

**Diagnosis**:
```go
func handleRequest(ctx *ext.Context) (interface{}, error) {
    log.Printf("Action: %s", ctx.Action)
    log.Printf("Params: %+v", ctx.Params)

    for key, value := range ctx.Params {
        log.Printf("Param %s: type=%T, value=%v", key, value, value)
    }

    // Your logic
}
```

**Solutions**:
1. Check parameter types (JSON numbers → float64)
2. Use type assertions with checks:
   ```go
   sid, ok := ctx.Params["sid"].(string)
   if !ok {
       return nil, fmt.Errorf("sid must be string")
   }
   ```
3. Handle optional parameters:
   ```go
   depth := 3  // default
   if d, ok := ctx.Params["depth"].(float64); ok {
       depth = int(d)
   }
   ```

## Debugging Techniques

### Logging Best Practices

```go
import (
    "log"
    "os"
)

func init() {
    // Set up structured logging
    log.SetFlags(log.LstdFlags | log.Lshortfile)

    // Optional: JSON logging
    // log.SetOutput(os.Stdout)
}

func handleRequest(ctx *ext.Context) (interface{}, error) {
    log.Printf("[INFO] Received request: action=%s, oid=%s", ctx.Action, ctx.OID)
    log.Printf("[DEBUG] Parameters: %+v", ctx.Params)

    // Your logic

    result := map[string]interface{}{"status": "success"}
    log.Printf("[INFO] Sending response: %+v", result)

    return result, nil
}
```

### Request Tracing

```go
import (
    "context"
    "time"
)

func handleRequest(ctx *ext.Context) (interface{}, error) {
    requestID := generateRequestID()
    start := time.Now()

    log.Printf("[%s] START action=%s", requestID, ctx.Action)
    defer func() {
        duration := time.Since(start)
        log.Printf("[%s] END duration=%v", requestID, duration)
    }()

    // Your logic

    return result, nil
}
```

### Webhook Payload Inspection

```go
func webhookHandler(w http.ResponseWriter, r *http.Request) {
    // Save payload to file for inspection
    body, _ := ioutil.ReadAll(r.Body)

    // Log to file
    f, _ := os.OpenFile("webhook.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    defer f.Close()

    f.WriteString(fmt.Sprintf("=== %s ===\n", time.Now()))
    f.WriteString(fmt.Sprintf("Headers: %+v\n", r.Header))
    f.WriteString(fmt.Sprintf("Body: %s\n\n", string(body)))

    // Continue processing
    r.Body = ioutil.NopCloser(bytes.NewReader(body))
}
```

### Performance Profiling

```go
import (
    "net/http/pprof"
    "runtime/pprof"
)

func main() {
    // Enable profiling endpoints
    go func() {
        mux := http.NewServeMux()
        mux.HandleFunc("/debug/pprof/", pprof.Index)
        mux.HandleFunc("/debug/pprof/cmdline", pprof.Cmdline)
        mux.HandleFunc("/debug/pprof/profile", pprof.Profile)
        http.ListenAndServe(":6060", mux)
    }()

    // Your extension code
}
```

Access profiles:
```bash
# CPU profile
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Memory profile
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine profile
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

## Performance Optimization

### Caching Configurations

```go
import (
    "sync"
    "time"
)

type ConfigCache struct {
    mu    sync.RWMutex
    data  map[string]CacheEntry
}

type CacheEntry struct {
    Config    map[string]interface{}
    ExpiresAt time.Time
}

func (c *ConfigCache) Get(oid string) (map[string]interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()

    entry, ok := c.data[oid]
    if !ok || time.Now().After(entry.ExpiresAt) {
        return nil, false
    }

    return entry.Config, true
}

func (c *ConfigCache) Set(oid string, config map[string]interface{}, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.data[oid] = CacheEntry{
        Config:    config,
        ExpiresAt: time.Now().Add(ttl),
    }
}

// Usage
var configCache = &ConfigCache{data: make(map[string]CacheEntry)}

func getConfig(oid string, sdk *limacharlie.SDK) (map[string]interface{}, error) {
    if config, ok := configCache.Get(oid); ok {
        return config, nil
    }

    config, err := sdk.Hive().Get("extension_configuration", "my-ext")
    if err != nil {
        return nil, err
    }

    configCache.Set(oid, config, 5*time.Minute)
    return config, nil
}
```

### Async Operations

```go
func handleScan(ctx *ext.Context) (interface{}, error) {
    sid := ctx.Params["sid"].(string)

    // Start async scan
    go func() {
        results := performLongScan(ctx.SDK, sid)

        // Store results in Hive for later retrieval
        ctx.SDK.Hive().Set("scan_results", sid, results)
    }()

    // Return immediately
    return map[string]interface{}{
        "status":  "started",
        "message": "Scan initiated",
    }, nil
}
```

### Connection Pooling

```go
import (
    "net/http"
    "time"
)

var httpClient = &http.Client{
    Timeout: 30 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}

// Use httpClient for all HTTP requests
resp, err := httpClient.Post(url, "application/json", body)
```

### Batch Processing

```go
func handleBatchScan(ctx *ext.Context) (interface{}, error) {
    targets := ctx.Params["targets"].([]interface{})

    // Process in batches
    batchSize := 10
    results := make([]interface{}, 0, len(targets))

    for i := 0; i < len(targets); i += batchSize {
        end := i + batchSize
        if end > len(targets) {
            end = len(targets)
        }

        batch := targets[i:end]
        batchResults := processBatch(ctx.SDK, batch)
        results = append(results, batchResults...)
    }

    return map[string]interface{}{
        "results": results,
    }, nil
}
```

This troubleshooting guide covers the most common issues and debugging techniques. For additional help, consult the LimaCharlie community Slack or contact answers@limacharlie.io.
