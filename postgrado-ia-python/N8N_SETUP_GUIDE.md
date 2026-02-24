# N8N Configuration Guide - RAG Chatbot for University Postgraduate Programs

## 📖 Overview

This guide provides step-by-step instructions to configure two main workflows in n8n:
1. **PDF Ingestion Workflow**: Processes PDFs and stores embeddings in ChromaDB
2. **Query Processing Workflow**: Handles user questions and generates responses

## 🔐 Prerequisites

Before starting, ensure:
- n8n is running at `http://localhost:5678`
- ChromaDB is accessible at `http://chromadb:8000`
- OpenAI API Key is configured
- RAG API is running at `http://rag-api:8000`

## 🔑 Step 1: Configure Credentials

### OpenAI API Credentials

1. **Navigate to Credentials**
   - Click on menu icon (≡)
   - Select "Credentials"
   - Click "Create New"

2. **Add OpenAI API Credential**
   - Select "OpenAI" from the list
   - Name: `OpenAI API`
   - API Key: `sk-xxxxxxxxxx` (your actual key)
   - Click "Create"

### HTTP Request Credentials (for ChromaDB)

1. **Create HTTP Auth**
   - Name: `ChromaDB Connection`
   - Authentication: None (for local ChromaDB)
   - URL: `http://chromadb:8000`

## 📥 Workflow 1: PDF Ingestion

### Purpose
Receives PDF files, processes them, generates embeddings, and stores in ChromaDB.

### Workflow Nodes

#### Node 1: Webhook Trigger
```
Name: Trigger - PDF Upload
Type: Webhook
```

Configuration:
- HTTP Method: `POST`
- Path: `/webhook/pdf-ingest`
- Authentication: None (or use API Key for production)
- Response: `Automatically send response`

#### Node 2: Validation
```
Name: Validate PDF File
Type: If Condition
```

Configuration:
- Condition: 
  ```
  {{ $json.filename && $json.filename.endsWith('.pdf') }}
  ```

#### Node 3: Read PDF Content
```
Name: Read PDF from Request
Type: HTTP Request
```

Configuration:
- Method: `POST`
- URL: `http://rag-api:8000/ingest/pdf`
- Headers:
  ```
  Content-Type: multipart/form-data
  ```
- Body (Form Data):
  - `file`: Binary file data from webhook

#### Node 4: Process Response
```
Name: Handle Ingestion Response
Type: If Condition
```

Configuration:
- Check if `{{ $json.success === true }}`

#### Node 5: Return Success
```
Name: Success Response
Type: Respond to Webhook
```

Configuration:
```json
{
  "status": "success",
  "message": "{{ $json.message }}",
  "filename": "{{ $json.file_name }}"
}
```

#### Node 6: Return Error
```
Name: Error Response
Type: Respond to Webhook
```

Configuration:
```json
{
  "status": "error",
  "message": "{{ $json.error }}"
}
```

### Workflow Structure

```
[Webhook] 
    ↓
[Validate PDF]
    ↓
[Read PDF] 
    ↓
[Handle Response]
    ├─ Success → [Return Success] → Webhook Response
    └─ Error → [Return Error] → Webhook Response
```

## 🔍 Workflow 2: Query Processing

### Purpose
Receives user questions via webhook, retrieves relevant context, and generates responses.

### Workflow Nodes

#### Node 1: Webhook Trigger
```
Name: Trigger - User Query
Type: Webhook
```

Configuration:
- HTTP Method: `POST`
- Path: `/webhook/query`
- Request Body (JSON):
  ```json
  {
    "question": "¿Cuáles son los requisitos de admisión?",
    "return_sources": true
  }
  ```

#### Node 2: Validate Query
```
Name: Validate Query Input
Type: If Condition
```

Configuration:
```
{{ $json.question && $json.question.length >= 3 }}
```

#### Node 3: Send Query to RAG API
```
Name: Query RAG API
Type: HTTP Request
```

Configuration:
- Method: `POST`
- URL: `http://rag-api:8000/query`
- Headers:
  ```
  Content-Type: application/json
  ```
- Body (JSON):
  ```json
  {
    "question": "{{ $json.question }}",
    "return_sources": "{{ $json.return_sources }}"
  }
  ```

#### Node 4: Format Response
```
Name: Format Response
Type: Function
```

Configuration - JavaScript:
```javascript
return {
  question: $('Query RAG API').item.json.question,
  answer: $('Query RAG API').item.json.answer,
  sources: $('Query RAG API').item.json.sources,
  timestamp: new Date().toISOString(),
  success: $('Query RAG API').item.json.success
};
```

#### Node 5: Send Response
```
Name: Send Response
Type: Respond to Webhook
```

Configuration:
```json
{
  "question": "{{ $json.question }}",
  "answer": "{{ $json.answer }}",
  "sources": "{{ $json.sources }}",
  "timestamp": "{{ $json.timestamp }}"
}
```

#### Node 6: Handle Errors
```
Name: Error Handler
Type: Respond to Webhook
```

Configuration:
```json
{
  "error": "Query processing failed",
  "details": "{{ $error.message }}"
}
```

### Workflow Structure

```
[Webhook]
    ↓
[Validate]
    ├─ Valid → [Query RAG API]
    │              ↓
    │         [Format Response]
    │              ↓
    │         [Send Response] → Webhook Response
    │
    └─ Invalid → [Error Handler] → Webhook Response
```

## 🔄 Workflow 3: Batch PDF Processing (Optional)

For processing multiple PDFs from a folder:

#### Node 1: Trigger
```
Type: Cron - Schedule at 2 AM daily
```

#### Node 2: Get Files from Directory
```
Type: Execute Command
Command: find /documents -name "*.pdf" -type f
```

#### Node 3: Loop Over Files
```
Type: Loop - For each file
```

#### Node 4: Ingest PDF
```
Type: HTTP Request
URL: http://rag-api:8000/ingest/pdf
```

#### Node 5: Log Results
```
Type: Set node
Result: Success/Failure log
```

## 📊 Testing the Workflows

### Test PDF Ingestion

```bash
curl -X POST http://localhost:5678/webhook/pdf-ingest \
  -F "file=@sample.pdf"
```

Expected Response:
```json
{
  "status": "success",
  "message": "PDF 'sample.pdf' successfully ingested",
  "filename": "sample.pdf"
}
```

### Test Query Processing

```bash
curl -X POST http://localhost:5678/webhook/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuáles son los horarios de atención?",
    "return_sources": true
  }'
```

Expected Response:
```json
{
  "question": "¿Cuáles son los horarios de atención?",
  "answer": "Basado en los documentos oficiales...",
  "sources": [
    {
      "source": "horarios.pdf",
      "page": 1,
      "content": "..."
    }
  ],
  "timestamp": "2024-02-23T15:30:00Z"
}
```

## 🔧 Advanced Configuration

### Enable Logging

Add to each workflow:
1. **Enable Workflow Logging**
   - Settings → Logging
   - Set log level: `Debug`

### Error Notifications

Add error handling nodes:
```
Error → Email Notification → Admin
```

### Rate Limiting

Use "Wait" node between requests:
```
[Request] → [Wait 500ms] → [Next Request]
```

### Caching Responses

Add "Cache" node for frequently asked questions:
```
[Query] → [Check Cache] → [Cache Hit] → Response
              ↓
          [Cache Miss] → [API Call] → [Store in Cache]
```

## 📈 Monitoring

### Health Check Workflow

Create a simple workflow to monitor service status:

1. **Trigger**: Cron every 5 minutes
2. **Check Health**:
   - HTTP Request: `GET http://rag-api:8000/health`
3. **Handle Response**:
   - If status = "healthy" → Continue
   - Else → Send alert email

### Metrics to Track

- **PDF Ingestion**: Number of PDFs processed per day
- **Query Processing**: Average response time
- **Error Rate**: Failed queries / total queries
- **Cache Hit Rate**: Cached responses / total responses

## 🐛 Troubleshooting

### ChromaDB Connection Failed

**Error**: `Cannot reach http://chromadb:8000`

**Solution**:
1. Check service name in docker-compose.yml
2. Verify network connectivity:
   ```bash
   docker network ls
   docker network inspect rag-network
   ```
3. Test connection from n8n container:
   ```bash
   docker exec postgrado-n8n curl http://chromadb:8000/api/v1
   ```

### OpenAI API Timeout

**Error**: `OpenAI API request timeout`

**Solution**:
1. Increase timeout in HTTP Request node: 30s
2. Check API rate limits
3. Verify API key is valid

### PDF Processing Fails

**Error**: `PDF validation failed`

**Solution**:
1. Verify file is valid PDF
2. Check file size < 50MB
3. Review logs in RAG API

## 📚 Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [ChromaDB API](https://docs.trychroma.com/)
- [OpenAI API Guide](https://platform.openai.com/docs/guides)
- [LangChain Documentation](https://python.langchain.com/)

## ✅ Checklist

Before going to production:

- [ ] Test PDF ingestion with sample documents
- [ ] Test query processing with various questions
- [ ] Configure error notifications
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Test failover scenarios
- [ ] Document custom workflows
- [ ] Train staff on workflow management
- [ ] Set up security (API keys, authentication)
- [ ] Performance test with expected load

---

**Last Updated**: February 2024
**Version**: 1.0
