# Complete Deployment Guide - RAG Chatbot for University Postgraduate Programs

## 🎯 Overview

This guide provides a complete step-by-step process to deploy the RAG Chatbot system on Debian Linux with Docker Compose.

**Deployment Time**: ~30-45 minutes
**System Requirements**: 
- CPU: 4+ cores
- RAM: 8GB minimum (16GB recommended)
- Disk: 50GB (for documents + database)
- OS: Debian 11/12 Linux

## 🔧 Phase 1: System Preparation

### Step 1.1: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 1.2: Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (avoid sudo for docker commands)
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker installation
docker --version
docker run hello-world
```

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### Step 1.3: Install Git (if not present)

```bash
sudo apt-get install -y git
git --version
```

### Step 1.4: Install Python 3.11 (for local development)

```bash
sudo apt-get install -y python3.11 python3.11-venv python3-pip
python3 --version
```

## 📂 Phase 2: Project Setup

### Step 2.1: Clone Repository

```bash
# Navigate to desired directory
cd /opt/postgrado-ia

# Clone the repository
git clone <repository-url> postgrado-ia-python
cd postgrado-ia-python
```

### Step 2.2: Create Project Structure

```bash
# Create necessary directories
mkdir -p documents logs postgres/data chromadb/data n8n/data

# Set proper permissions
chmod 755 documents logs
```

### Step 2.3: Configure Environment Variables

```bash
# Copy environment template
cp .env .env.production

# Edit with production values
nano .env.production
```

**Critical environment variables to update:**

```env
# API Keys - KEEP SECURE!
OPENAI_API_KEY=sk-your-real-api-key-here

# Database Credentials - Use strong passwords
DB_USER=postgrado_db_user
DB_PASSWORD=generate_with_$(openssl rand -base64 32)
POSTGRES_PASSWORD=generate_with_$(openssl rand -base64 32)

# n8n Encryption (generate: openssl rand -base64 32)
N8N_ENCRYPTION_KEY=generate_with_$(openssl rand -base64 32)

# Environment
ENVIRONMENT=production

# LLM Configuration
LLM_MODEL=gpt-4
TEMPERATURE=0.3
MAX_TOKENS=1000
```

**Generate secure passwords:**

```bash
# Generate secure credentials
echo "DB_PASSWORD=$(openssl rand -base64 32)" >> .env.production
echo "N8N_ENCRYPTION_KEY=$(openssl rand -base64 32)" >> .env.production
```

### Step 2.4: Create Required Directories with Permissions

```bash
# Create and configure directories
mkdir -p postgres/data
mkdir -p chromadb/data
mkdir -p n8n/data
mkdir -p documents
mkdir -p logs

# Set permissions for Docker volumes
sudo chown 999:999 postgres/data  # PostgreSQL user
sudo chown 999:999 chromadb/data  # ChromaDB user
sudo chown 1000:1000 n8n/data    # n8n user
sudo chown 1000:1000 logs         # Application logs

# Set read/write permissions
chmod 755 documents logs
```

## 🚀 Phase 3: Docker Deployment

### Step 3.1: Build Docker Image

```bash
# Navigate to project directory
cd /opt/postgrado-ia/postgrado-ia-python

# Build the RAG API Docker image
docker-compose build rag-api

# Verify build
docker images | grep postgrado
```

### Step 3.2: Start Services (Initial Deployment)

```bash
# Start all services in background
docker-compose up -d

# Monitor startup (Ctrl+C to exit)
docker-compose logs -f
```

Expected startup sequence (takes ~2-3 minutes):
1. PostgreSQL initializes database
2. ChromaDB starts vector engine
3. n8n initializes and connects to PostgreSQL
4. RAG API builds and starts

### Step 3.3: Verify Services Health

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                 STATUS              PORTS
# postgrado-postgres   Up (healthy)        5432/tcp
# postgrado-chromadb   Up (healthy)        8001->8000/tcp
# postgrado-n8n        Up (healthy)        5678/tcp
# postgrado-rag-api    Up (healthy)        8000/tcp
```

### Step 3.4: Health Checks

```bash
# Check PostgreSQL
docker-compose exec postgres psql -U postgrado_db_user -d n8n -c "SELECT version();"

# Check ChromaDB
curl http://localhost:8001/api/v1

# Check n8n
curl http://localhost:5678/healthz

# Check RAG API
curl http://localhost:8000/health
```

All should return success responses.

## ⚙️ Phase 4: Initial Configuration

### Step 4.1: Access n8n Web Interface

1. Open browser: `http://localhost:5678`
2. Create admin user (email + password)
3. Accept license

### Step 4.2: Configure API Credentials in n8n

1. **OpenAI Integration**
   - Settings → Credentials
   - Create New → OpenAI
   - Paste API Key
   - Test connection

2. **Test Webhook**
   - Settings → Webhooks
   - Create test webhook endpoint

### Step 4.3: Verify RAG API

```bash
# Test API endpoints
curl -X GET http://localhost:8000/health

# Expected response:
# {"status":"healthy","vector_db_connected":true,"llm_available":true}
```

### Step 4.4: Upload Sample Documents

```bash
# Copy sample PDFs to documents folder
cp /path/to/requirements.pdf ./documents/
cp /path/to/calendar.pdf ./documents/

# Ingest a PDF
curl -X POST http://localhost:8000/ingest/pdf \
  -F "file=@./documents/requirements.pdf"
```

## 📚 Phase 5: n8n Workflow Setup

### Step 5.1: Create PDF Ingestion Workflow

Follow the detailed instructions in [N8N_SETUP_GUIDE.md](N8N_SETUP_GUIDE.md)

**Quick Setup:**
1. Create new workflow
2. Add Webhook trigger (POST /webhook/pdf-ingest)
3. Add HTTP request to RAG API ingestion endpoint
4. Add response nodes
5. Activate workflow

### Step 5.2: Create Query Processing Workflow

Follow the detailed instructions in [N8N_SETUP_GUIDE.md](N8N_SETUP_GUIDE.md)

**Quick Setup:**
1. Create new workflow
2. Add Webhook trigger (POST /webhook/query)
3. Add validation node
4. Add HTTP request to RAG API query endpoint
5. Format and return response
6. Activate workflow

### Step 5.3: Test Workflows

```bash
# Test PDF ingestion workflow
curl -X POST http://localhost:5678/webhook/pdf-ingest \
  -F "file=@./documents/test.pdf"

# Test query workflow
curl -X POST http://localhost:5678/webhook/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cuáles son los requisitos?",
    "return_sources": true
  }'
```

## 🔐 Phase 6: Security Hardening

### Step 6.1: Network Security

```bash
# Create firewall rules (if using ufw)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow only Docker services on specific ports
sudo ufw allow from 0.0.0.0/0 to any port 8000  # RAG API (restrict as needed)
sudo ufw allow from 0.0.0.0/0 to any port 5678  # n8n (restrict as needed)

# Internal ports (only from localhost for production)
sudo ufw allow from 127.0.0.1 to any port 5432  # PostgreSQL
sudo ufw allow from 127.0.0.1 to any port 8001  # ChromaDB
```

### Step 6.2: API Authentication (n8n)

1. **Enable API Key Authentication**
   - n8n → Settings → API Key
   - Generate secure API key
   - Add to environment: `N8N_API_KEY=your_key`

2. **Secure Webhook Endpoints**
   - Add authentication token to webhook URLs
   - Validate requests in n8n

### Step 6.3: Database Security

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U postgrado_db_user n8n > backup_$(date +%Y%m%d).sql

# Verify backup
ls -lh backup_*.sql
```

### Step 6.4: SSL/TLS Setup (Production)

```bash
# Install certbot for Let's Encrypt
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure in docker-compose.yml with reverse proxy (nginx)
```

## 📊 Phase 7: Monitoring & Logging

### Step 7.1: View Logs

```bash
# RAG API logs
docker-compose logs rag-api -f

# n8n logs
docker-compose logs n8n -f

# PostgreSQL logs
docker-compose logs postgres

# ChromaDB logs
docker-compose logs chromadb
```

### Step 7.2: Monitor Resource Usage

```bash
# Real-time monitoring
docker stats

# Or use specific container
docker stats postgrado-rag-api
```

### Step 7.3: Setup Log Aggregation (Optional)

Create `monitoring-docker-compose.yml`:

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## 🔄 Phase 8: Operational Tasks

### Step 8.1: Daily Operations

```bash
# Check service status
docker-compose ps

# View recent logs
docker-compose logs --tail=50 rag-api

# Monitor performance
docker stats
```

### Step 8.2: Document Management

```bash
# Organize PDF documents
mkdir -p documents/{maestrias,doctorados,especializaciones,reglamentos}

# Move documents
mv documents/*.pdf documents/maestrias/

# Ingest batch of documents
for file in documents/maestrias/*.pdf; do
  curl -X POST http://localhost:8000/ingest/pdf \
    -F "file=@$file"
  sleep 2  # Avoid rate limiting
done
```

### Step 8.3: Regular Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U postgrado_db_user n8n \
  > $BACKUP_DIR/n8n_database.sql

# Backup ChromaDB data
cp -r chromadb/data $BACKUP_DIR/chromadb_backup

# Backup configurations
cp .env.production $BACKUP_DIR/

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR/
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh
./backup.sh
```

### Step 8.4: Restart Strategies

```bash
# Restart specific service
docker-compose restart rag-api

# Restart all services
docker-compose restart

# Full redeploy (with data persistence)
docker-compose down
docker-compose up -d

# Complete reset (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

## 🐛 Phase 9: Troubleshooting

### Common Issues

#### Issue: Services don't start

```bash
# Check logs
docker-compose logs

# Verify environment variables
cat .env.production

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

#### Issue: API returns 503 (Service Unavailable)

```bash
# Check if ChromaDB is running
docker-compose logs chromadb

# Verify connectivity from API container
docker-compose exec rag-api curl http://chromadb:8000/api/v1
```

#### Issue: PDF ingestion fails

```bash
# Check file format
file documents/test.pdf

# Verify file permissions
ls -la documents/

# Check API logs
docker-compose logs rag-api | grep -i error
```

#### Issue: OpenAI API errors

```bash
# Verify API key
echo $OPENAI_API_KEY

# Test OpenAI connectivity
docker-compose exec rag-api python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('OK')"
```

## 📈 Phase 10: Performance Tuning

### Optimize ChromaDB

```yaml
# In docker-compose.yml
environment:
  - CHROMA_CHUNK_SIZE=256
  - CHROMA_QUERY_SIZE=1024
```

### Optimize LLM Requests

```python
# In app/config.py
TEMPERATURE=0.2  # Lower = faster response
MAX_TOKENS=500   # Reduce if not needed
RETRIEVAL_K=3    # Fewer results = faster
```

### Monitor Performance

```bash
# Response time tests
time curl http://localhost:8000/health

# Load testing (basic)
for i in {1..10}; do
  curl http://localhost:8000/health &
done
wait
```

## ✅ Deployment Checklist

- [ ] Debian Linux server ready (4+ CPU, 8GB RAM, 50GB disk)
- [ ] Docker & Docker Compose installed and verified
- [ ] Repository cloned to /opt/postgrado-ia/
- [ ] Environment variables configured (.env.production)
- [ ] Directory permissions set correctly
- [ ] docker-compose up -d executed successfully
- [ ] All services healthy (docker-compose ps)
- [ ] Health endpoints respond (curl /health)
- [ ] n8n admin user created
- [ ] OpenAI credentials configured
- [ ] PDF ingestion workflow created and tested
- [ ] Query processing workflow created and tested
- [ ] Sample documents uploaded and working
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring/logging configured
- [ ] Load testing completed
- [ ] Documentation updated with production details
- [ ] Team trained on operations
- [ ] Disaster recovery plan documented

## 📞 Support & Maintenance

**Regular Maintenance Schedule:**
- Daily: Check service status, review error logs
- Weekly: Backup databases, review performance metrics
- Monthly: Update Docker images, test disaster recovery
- Quarterly: Security audit, capacity planning review

**Escalation Contacts:**
- Technical: [DevOps Team Email]
- OpenAI Issues: [OpenAI Support]
- Database Issues: [DBA Contact]

---

**Last Updated**: February 2024
**Version**: 1.0
**Maintainer**: DevOps Team
