# RAG Chatbot para Asesoría de Posgrados

Sistema de Chatbot con arquitectura RAG (Retrieval-Augmented Generation) para automatizar la asesoría de aspirantes a programas de posgrado.

## 🎯 Características

- **Procesamiento de PDFs**: Ingesta automática de documentos oficiales (reglamentos, calendarios, guías)
- **Base de Datos Vectorial**: Almacenamiento de embeddings con ChromaDB
- **Generación Aumentada por Recuperación**: Uso de GPT-4 con contexto relevante
- **Anti-Alucinaciones**: System prompt optimizado que previene respuestas fuera de contexto
- **Latencia Optimizada**: Respuestas en menos de 5 segundos
- **API REST**: Endpoints para ingesta de documentos y consultas
- **Containerización**: Docker Compose para despliegue en Debian
- **Orquestación**: n8n para flujos de trabajo automáticos
- **Testing Completo**: Pruebas unitarias e integración

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        n8n (Orquestador)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PDF Ingesta  │  │   Chunks     │  │   Embeddings     │  │
│  │  (Webhook)   │  │  + Overlap   │  │   (OpenAI)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│           ↓                ↓                    ↓            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        ChromaDB (Base de Datos Vectorial)            │  │
│  │     (Almacenamiento de embeddings + metadata)        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             ↑
┌─────────────────────────────────────────────────────────────┐
│              API FastAPI (RAG Chatbot Backend)              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Retriever  │  │ LLM (GPT-4)  │  │   Response       │  │
│  │  (Consultas) │  │  Processor   │  │   Generator      │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                             ↑
┌─────────────────────────────────────────────────────────────┐
│           Frontend / Cliente (Webhook de n8n)               │
│     (UI Web, Chat, Integración con sistemas externos)       │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Requisitos Previos

- Docker y Docker Compose (v2.0+)
- Python 3.11+ (para desarrollo local)
- Debian/Linux (recomendado para producción)
- API Key de OpenAI (para GPT-4)
- Espacio en disco: Mínimo 10GB

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd postgrado-ia-python
```

### 2. Configurar Variables de Entorno

```bash
cp .env .env.local
# Editar .env.local con tus credenciales
```

**Variables necesarias:**

```env
# API Keys
OPENAI_API_KEY=sk-xxxxxxxxxxxx

# Database
DB_USER=n8n_user
DB_PASSWORD=tu_contraseña_segura
N8N_ENCRYPTION_KEY=tu_clave_encriptacion

# LLM
LLM_MODEL=gpt-4
TEMPERATURE=0.3
MAX_TOKENS=1000
RETRIEVAL_K=5
```

### 3. Levantar los Servicios

```bash
docker-compose up -d
```

Esto iniciará:
- **PostgreSQL** (puerto 5432): Base de datos para n8n
- **ChromaDB** (puerto 8001): Base de datos vectorial
- **n8n** (puerto 5678): Orquestador de flujos
- **RAG API** (puerto 8000): API del chatbot

### 4. Verificar Servicios

```bash
# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f rag-api
```

## 📚 Uso

### API Endpoints

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "vector_db_connected": true,
  "llm_available": true
}
```

#### 2. Realizar una Consulta

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d {
    "question": "¿Cuáles son los requisitos para el programa de Maestría en IA?",
    "return_sources": true
  }
```

**Respuesta:**
```json
{
  "success": true,
  "question": "¿Cuáles son los requisitos para el programa de Maestría en IA?",
  "answer": "Según los documentos oficiales, los requisitos incluyen...",
  "sources": [
    {
      "source": "requisitos_maestria.pdf",
      "page": 2,
      "content": "Los requisitos incluyen..."
    }
  ]
}
```

#### 3. Ingestar un PDF

```bash
curl -X POST http://localhost:8000/ingest/pdf \
  -F "file=@/ruta/al/documento.pdf"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "PDF 'documento.pdf' successfully ingested",
  "file_name": "documento.pdf"
}
```

### Documentación Interactiva

Accede a la documentación API en:
```
http://localhost:8000/docs
```

## ⚙️ Configuración de n8n

### Flujo de Ingesta (PDF → ChromaDB)

1. **Trigger**: Webhook que recibe PDF
2. **Validación**: Verifica que sea PDF válido
3. **Procesamiento**:
   - Lectura del PDF
   - División en chunks (1000 caracteres con overlap de 200)
   - Generación de embeddings (OpenAI)
4. **Almacenamiento**: Inserta en ChromaDB con metadata

### Flujo de Consulta (Webhook → Respuesta)

1. **Trigger**: Webhook recibe pregunta
2. **Búsqueda**: Consulta ChromaDB para documentos relevantes
3. **Construcción del Prompt**: Combina sistema + contexto + pregunta
4. **Generación**: Llama a GPT-4
5. **Respuesta**: Retorna al cliente

### Pasos de Configuración

1. Accede a n8n: `http://localhost:5678`
2. Crea un nuevo workflow
3. Agrega nodos según los flujos descritos arriba
4. Configura credenciales (OpenAI API Key)
5. Activa el workflow

## 🧠 System Prompt Optimizado

El prompt del sistema está diseñado para:

✅ **Evitar Alucinaciones**
- Solo responde basado en documentación oficial
- Rechaza preguntas fuera del contexto de posgrados
- Sugiere contactar a la oficina si no hay información

✅ **Mantener Tono Profesional**
- Amable y empático con aspirantes
- Respuestas claras y estructuradas
- Ofrece múltiples opciones cuando es relevante

✅ **Cumplir Requisitos de Latencia**
- Timeout de 5 segundos máximo
- Caché de respuestas frecuentes
- Optimización de búsquedas vectoriales

## 🗂️ Estructura de Metadata

ChromaDB almacena embeddings con metadata:

```python
{
  "source_file": "requisitos_maestria.pdf",
  "file_type": "pdf",
  "program": "Maestría en Inteligencia Artificial",
  "uploaded_at": "1708705200",
  "section": "Requisitos de Admisión",
  "page": 2
}
```

Esto permite filtrado avanzado de búsquedas.

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Todas las pruebas
pytest

# Con coverage
pytest --cov=app tests/

# Pruebas específicas
pytest tests/test_rag_logic.py -v

# Solo pruebas unitarias
pytest -m unit

# Con output detallado
pytest -vv --tb=long
```

### Cobertura de Tests

El proyecto incluye pruebas para:

- ✅ Validación de PDFs
- ✅ Validación de consultas
- ✅ Ingesta de documentos
- ✅ Recuperación de contexto
- ✅ Generación de respuestas
- ✅ Endpoints de API
- ✅ Manejo de errores
- ✅ Anti-alucinaciones
- ✅ Latencia (<5s)

## 📊 Estructura de Directorios

```
postgrado-ia-python/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── config.py            # Configuración
│   ├── engine/
│   │   ├── ingest.py        # Ingesta de PDFs
│   │   └── query.py         # Procesamiento de consultas
│   └── utils/
│       ├── logging_config.py
│       └── validators.py    # Validación de entrada
├── tests/
│   ├── test_rag_logic.py    # Pruebas RAG
│   ├── test_api.py          # Pruebas API
│   └── conftest.py          # Configuración pytest
├── documents/               # PDFs para ingesta
├── docker-compose.yml       # Orquestación de servicios
├── Dockerfile              # Imagen del API
├── requirements.txt        # Dependencias Python
├── pytest.ini             # Configuración pytest
├── .env                   # Variables de entorno
└── README.md
```

## 🔒 Seguridad

### Validaciones Implementadas

1. **Validación de Archivos**
   - Solo acepta PDFs válidos
   - Máximo 50MB por archivo
   - Verifica MIME type

2. **Validación de Entrada**
   - Mínimo 3 caracteres en queries
   - Máximo 1000 caracteres
   - Sanitización básica

3. **Secretos y Credenciales**
   - API Keys en variables de entorno
   - Nunca se loguean credenciales
   - Encriptación de datos en tránsito (HTTPS en producción)

## 📈 Performance

### Latencia Target

| Operación | Target | Actual |
|-----------|--------|--------|
| Consulta simple | <5s | ~2-3s |
| Ingesta de PDF | <30s | ~10-15s |
| Health check | <1s | ~200ms |

### Optimizaciones

- ChromaDB en-memory caché
- Compresión de embeddings
- Chunking con overlap para contexto
- Batch processing de PDFs

## 🛠️ Troubleshooting

### ChromaDB no conecta

```bash
docker-compose logs chromadb
docker-compose restart chromadb
```

### PostgreSQL no inicia

```bash
docker volume rm postgrado-ia-python_postgres_data
docker-compose up postgres
```

### OpenAI API Error

```bash
# Verificar API Key
echo $OPENAI_API_KEY

# Revisar logs
docker-compose logs rag-api | grep OpenAI
```

### Tests fallan

```bash
# Limpiar caché de pytest
rm -rf .pytest_cache

# Reinstalar dependencias
pip install -r requirements.txt

# Ejecutar con debug
pytest -vv --tb=long
```

## 📝 Licencia

Este proyecto es confidencial. Uso interno solamente.

## 👥 Soporte

Para reportar problemas o sugerencias:
- Email: soporte@universidad.edu
- Portal: https://github.com/universidadposgrados/rag-chatbot

## 🔄 Actualización de Documentos

Para actualizar la base de datos de vectores:

```bash
# 1. Colocar PDFs en ./documents/
# 2. Ejecutar ingesta
curl -X POST http://localhost:8000/ingest/pdf \
  -F "file=@./documents/nuevo_documento.pdf"

# 3. Verificar ingesta
docker-compose logs rag-api
```

---

**Última actualización:** Febrero 2024
**Versión:** 0.1.0
