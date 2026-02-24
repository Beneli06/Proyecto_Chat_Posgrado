# System Prompt & Vector Database Structure Guide

## 🎯 Optimized System Prompt for Postgraduate Advisor Chatbot

### Design Principles

1. **Ethical & Transparent**: No hallucinations, clear source attribution
2. **Professional Tone**: Respectful and empathetic with applicants
3. **Accurate Information**: Only responds based on official documentation
4. **Actionable Guidance**: Provides next steps when needed

### Complete System Prompt (Spanish)

```
Eres un asistente experto en programas de posgrado de [NOMBRE DE UNIVERSIDAD]. 
Tu rol es proporcionar información precisa, ética y amable a los aspirantes a 
nuestros programas de maestría, doctorado y especialización.

═══════════════════════════════════════════════════════════════════════════════

INSTRUCCIONES CRÍTICAS - ANTI-ALUCINACIONES:

1. 🚫 PROHIBIDO INVENTAR INFORMACIÓN
   - SOLO responde preguntas basadas en la documentación oficial de la Universidad
   - Si la información NO está en los documentos, debes decir explícitamente:
     "No tengo información disponible sobre esto. Te recomiendo contactar 
      directamente a la oficina de posgrados en: [email/teléfono]"
   - NUNCA especules, asumas o inventes datos

2. ✅ REGLAS DE ORO PARA RESPUESTAS
   - Cita siempre la fuente del documento (programa, fecha, página)
   - Si hay múltiples respuestas, presenta todas las opciones
   - Sugiere alternativas cuando la información es parcial
   - Sé honesto si faltan detalles

3. 🎯 MANEJO DE CASOS ESPECIALES
   - Preguntas fuera de tema: "Mi expertise es en posgrados de [Universidad]. 
     Para otras consultas, por favor contacta al departamento correspondiente"
   - Preguntas controvertidas: "Entiendo tu pregunta. Basado en los documentos 
     oficiales, [respuesta factual]"
   - Cambios recientes: "La información más reciente que tengo es de [fecha]. 
     Te recomiendo verificar con la oficina de posgrados por actualizaciones"

═══════════════════════════════════════════════════════════════════════════════

ESTILO DE COMUNICACIÓN:

4. 📝 ESTRUCTURA DE RESPUESTAS
   - Inicia con un saludo breve y cordial
   - Responde de forma clara y ordenada (puntos, listas cuando sea relevante)
   - Incluye ejemplos concretos si aplica
   - Termina con una pregunta de seguimiento o llamada a acción

5. 💬 TONO Y LENGUAJE
   - Profesional pero accesible (evita jerga muy técnica)
   - Empático: "Entiendo que este es un momento importante en tu carrera"
   - Proactivo: "¿Hay algo más que quieras saber sobre [programa]?"
   - Multilingüe si aplica (responder en el idioma del usuario)

6. ⏱️ RESTRICCIONES DE CONTENIDO
   - Máximo 500 palabras por respuesta (sé conciso)
   - Si la respuesta requiere más información, sugiere contactar directamente
   - No hagas promesas sobre fechas límites futuras
   - No garantices aceptación ni tomes decisiones de admisión

═══════════════════════════════════════════════════════════════════════════════

CONTEXTO DE RESPUESTA:

{context}

═══════════════════════════════════════════════════════════════════════════════

PREGUNTA DEL USUARIO:

{question}

═══════════════════════════════════════════════════════════════════════════════

RESPUESTA:
```

### Customization Variables

Reemplazar los siguientes placeholders:
- `[NOMBRE DE UNIVERSIDAD]`: Nombre oficial
- `[email/teléfono]`: Contacto de posgrados
- `[programa]`: Nombre del programa

### Example Responses

#### ✅ Correct Response (Based on Context)

**Usuario**: "¿Cuáles son los requisitos para el programa de Maestría en IA?"

**Respuesta Ideal**:
```
Según el documento oficial "Requisitos de Admisión - Maestría en Inteligencia 
Artificial (actualizado en enero 2024)", los requisitos son:

1. Pregrado completado en área relacionada
2. Promedio mínimo de 3.5/5.0
3. TOEFL (mínimo 550) o IELTS (mínimo 6.5)
4. Carta de motivación
5. Referencia de profesor

Para más detalles, puedes revisar la página 3 del documento o contactar a:
📧 posgrados@universidad.edu
📞 +57-1-XXXX-XXXX
```

#### ❌ Incorrect Response (Hallucination)

**Usuario**: "¿Garantizan empleo después del programa?"

**Respuesta INCORRECTA** (❌ NO HACER):
```
Sí, el 95% de nuestros egresados consiguen empleo en 3 meses.
```

**Respuesta CORRECTA** (✅ HACER):
```
No tengo información en los documentos oficiales sobre garantías de empleo. 
Lo que sí puedo decirte es que según el reporte de egresados (2023), 
el 87% de egresados reportó que el programa mejoró sus oportunidades laborales.

Para información específica sobre bolsa de empleo o convenios con empresas, 
te recomiendo contactar directamente a:
📧 empleabilidad@universidad.edu
```

## 🗂️ Vector Database Metadata Structure

### ChromaDB Schema

```python
{
  # Document Identifiers
  "id": "doc_maestria_ia_req_001",
  
  # Content Metadata
  "metadata": {
    # Program Information
    "program_name": "Maestría en Inteligencia Artificial",
    "program_code": "MIT-2024",
    "program_level": "Master",  # Master, PhD, Specialization
    
    # Document Information
    "document_type": "requirements",  # requirements, calendar, regulations, faq
    "document_name": "Requisitos de Admisión",
    "document_version": "2.1",
    "last_updated": "2024-01-15",
    
    # Source Information
    "source_file": "requisitos_maestria_ia.pdf",
    "source_url": "https://universidad.edu/docs/requisitos_maestria_ia.pdf",
    "page_number": 3,
    "section": "Requisitos Académicos",
    
    # Organizational Data
    "department": "Escuela de Posgrados",
    "faculty": "Ingeniería",
    "academic_year": "2024-2025",
    
    # Content Classification
    "content_category": "admission",  # admission, curriculum, schedule, fees, other
    "keywords": ["requisitos", "admisión", "TOEFL", "GPA"],
    "language": "es",  # es, en, pt
    
    # Quality Metrics
    "confidence_score": 0.95,  # 0.0-1.0
    "is_official": true,  # Only official documents
    "validation_status": "approved",  # approved, pending, deprecated
    
    # Temporal Data
    "effective_date": "2024-01-15",
    "expiration_date": "2024-12-31",
    "created_at": "2024-01-15T10:30:00Z",
    "ingested_at": "2024-01-15T10:35:00Z"
  },
  
  # Document Content (vectorized)
  "content": "Los requisitos para el programa de Maestría en Inteligencia Artificial incluyen..."
}
```

### Metadata Hierarchy

```
University
├── Program (Maestría en IA)
│   ├── Document Type (Requisitos)
│   │   ├── Section (Requisitos Académicos)
│   │   │   └── Chunk (Requirement detail)
│   │   └── Section (Requisitos de Idioma)
│   │       └── Chunk (Language requirement)
│   ├── Document Type (Calendario)
│   │   └── Chunk (Important dates)
│   └── Document Type (Reglamentos)
│       └── Chunk (Academic rules)
└── Program (Doctorado en IA)
    └── ...
```

### Filtering Queries

#### Example 1: Get all requirements for a specific program

```python
results = vector_store.query(
    query_embedding=embeddings.embed("requisitos admisión"),
    where={
        "program_name": "Maestría en Inteligencia Artificial",
        "document_type": "requirements"
    },
    n_results=10
)
```

#### Example 2: Get only validated, current documents

```python
results = vector_store.query(
    query_embedding=embeddings.embed("horarios de clases"),
    where={
        "$and": [
            {"is_official": True},
            {"validation_status": "approved"},
            {"expiration_date": {"$gte": datetime.now().isoformat()}}
        ]
    },
    n_results=5
)
```

#### Example 3: Multi-program query

```python
results = vector_store.query(
    query_embedding=embeddings.embed("costo del programa"),
    where={
        "program_level": {"$in": ["Master", "PhD"]},
        "content_category": "fees"
    },
    n_results=10
)
```

### Ingestion Pipeline with Metadata

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.engine.ingest import PDFIngestionEngine

engine = PDFIngestionEngine()

# Define metadata for document
metadata = {
    "program_name": "Maestría en Inteligencia Artificial",
    "program_code": "MIT-2024",
    "document_type": "requirements",
    "document_name": "Requisitos de Admisión",
    "last_updated": "2024-01-15",
    "source_file": "requisitos_maestria_ia.pdf",
    "department": "Escuela de Posgrados",
    "is_official": True,
    "keywords": ["requisitos", "admisión", "TOEFL"]
}

# Ingest PDF with metadata
success = engine.ingest_pdf(
    pdf_path="./documents/requisitos_maestria_ia.pdf",
    metadata=metadata
)
```

### Query Strategy

#### 1. Direct Search (Most Common)

```python
# User asks: "¿Cuáles son los requisitos?"
query_results = engine.vector_store.similarity_search(
    "requisitos de admisión",
    k=5
)
# Returns top 5 most relevant chunks with metadata
```

#### 2. Semantic Search with Filters

```python
# User asks: "¿Qué requisitos tiene el doctorado?"
query_results = engine.vector_store.query(
    "requisitos académicos",
    where={"program_level": "PhD"},
    k=5
)
# Returns filtered results
```

#### 3. Program-Specific Search

```python
# User asks: "¿Cuál es el costo de la maestría en IA?"
query_results = engine.vector_store.query(
    "costo matrícula arancel",
    where={
        "program_name": "Maestría en Inteligencia Artificial",
        "content_category": "fees"
    },
    k=3
)
```

## 📊 Sample Data Structure

### Document Index Example

```json
{
  "documents": [
    {
      "id": "doc_req_mia_001",
      "program": "Maestría en IA",
      "type": "requirements",
      "content": "Requisito 1: Profesional con pregrado en...",
      "metadata": {
        "section": "Academic Requirements",
        "page": 1,
        "updated": "2024-01-15",
        "official": true
      }
    },
    {
      "id": "doc_req_mia_002",
      "program": "Maestría en IA",
      "type": "requirements",
      "content": "Requisito 2: Dominio del idioma inglés...",
      "metadata": {
        "section": "Language Requirements",
        "page": 2,
        "updated": "2024-01-15",
        "official": true
      }
    }
  ]
}
```

## 🔍 Best Practices

1. **Keep metadata consistent** across all documents
2. **Use ISO 8601** for dates (YYYY-MM-DD)
3. **Version control** documents with version numbers
4. **Regular updates** of expiration dates
5. **Quality scores** for search ranking
6. **Backup strategy** for vector database
7. **Monitor query performance** with logs

---

**Last Updated**: February 2024
**Version**: 1.0
