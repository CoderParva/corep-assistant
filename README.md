# COREP CR1 Reporting Assistant

## Overview
An LLM-assisted regulatory reporting prototype for UK banks subject to PRA Rulebook. This tool automates COREP CR1 (Credit Risk - Standardised Approach) template generation using RAG (Retrieval-Augmented Generation) and structured LLM outputs.

## Features
-  **RAG System**: Retrieves relevant PRA Rulebook articles using semantic search
-  **LLM Integration**: Extracts structured data from natural language queries using Groq (Llama 3.3)
-  **Validation Engine**: Validates exposures, risk weights, and RWA calculations
-  **Template Generation**: Exports COREP CR1 templates to Excel
-  **Audit Trail**: Provides regulatory justification for each classification
-  **Web Interface**: Interactive Streamlit UI for easy use

## Architecture
```
User Query → RAG Retrieval → LLM Processing → Structured Output → Validation → Excel Export
                ↓
         PRA Rulebook
      (Vector Database)
```

## Tech Stack
- **Python 3.13**
- **LLM**: Groq API (Llama 3.3 70B)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: NumPy cosine similarity
- **UI**: Streamlit
- **Data Processing**: Pandas, Pydantic
- **Export**: openpyxl

## Installation

### Prerequisites
- Python 3.11+ (3.13 recommended)
- Groq API key (free at https://console.groq.com/)

### Setup

1. **Clone the repository**
```bash
cd corep-assistant
```

2. **Create virtual environment**
```bash
py -3.13 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

3. **Install dependencies**
```bash
pip install --upgrade pip setuptools wheel
pip install numpy==2.1.0
pip install regex==2024.11.6
pip install sentence-transformers==3.3.1
pip install streamlit==1.39.0
pip install groq==0.4.1
pip install pandas openpyxl python-dotenv pydantic requests beautifulsoup4 pypdf2 langchain langchain-groq
```

4. **Configure API key**
Create a `.env` file in project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

5. **Process regulatory documents**
```bash
python -m src.retrieval.document_processor
```

## Usage

### Run the Application
```bash
streamlit run src/ui/app.py
```

The app will open in your browser at `http://localhost:8501`

### Example Queries

Enter exposures in natural language:
- "£50 million in unrated corporate exposures"
- "£100M residential mortgages"
- "£200M UK central government bonds"
- "£75M exposures to rated institutions, credit quality step 2"

The system will:
1. Retrieve relevant PRA Rulebook articles
2. Determine exposure class and risk weight
3. Calculate RWA
4. Show regulatory justification
5. Validate calculations

### Export Options
- **Excel Template**: Download populated CR1 template
- **Audit Trail**: Download detailed regulatory citations

## Project Structure
```
corep-assistant/
├── data/
│   ├── raw/
│   │   └── sample_pra_corpus.json    # PRA Rulebook excerpts
│   └── processed/
│       ├── chunks.pkl                 # Processed document chunks
│       └── outputs/                   # Excel exports & audit trails
├── src/
│   ├── retrieval/
│   │   ├── document_processor.py      # Document chunking & indexing
│   │   └── retriever.py               # Semantic search
│   ├── generation/
│   │   └── llm_generator.py           # LLM integration
│   ├── validation/
│   │   ├── validator.py               # Data validation
│   │   └── template_exporter.py       # Excel export
│   ├── ui/
│   │   └── app.py                     # Streamlit interface
│   └── schemas.py                     # Data models
├── .env                                # API keys (not committed)
├── requirements.txt
└── README.md
```

## Test Scenarios

The prototype has been tested with:

1. **Unrated Corporates** (100% risk weight)
2. **Residential Mortgages** (35% risk weight)
3. **Central Government** (0% risk weight)
4. **Commercial Real Estate** (100% risk weight)
5. **Rated Institutions** (20-150% based on credit quality)

## Validation Rules

The system validates:
-  Exposure values > 0
-  Risk weights within valid range (0-1250%)
-  RWA calculation accuracy
-  Total exposure = sum of rows
-  Total RWA = sum of row RWAs
-  Warns if regulatory references missing

## Limitations

### Scope Constraints
- **Single Template**: Only CR1 (Credit Risk - Standardised Approach)
- **Limited Articles**: Uses sample PRA Rulebook excerpts (Articles 112-125, 114, 124)
- **No IRB Approach**: Does not handle Internal Ratings-Based approach
- **Basic Validation**: Production systems need comprehensive cross-checks

### Technical Limitations
- **LLM Hallucination Risk**: May occasionally misclassify edge cases
- **No Human Review Loop**: Requires manual verification for production use
- **Point-in-Time Data**: PRA Rulebook snapshot as of Q1 2025
- **Simple Retrieval**: Uses basic semantic search (no hybrid search)
- **No Multi-Currency**: Assumes GBP only

### Not Production-Ready
This is a **prototype demonstration**. Production systems require:
- Comprehensive PRA Rulebook coverage
- Multi-template support (all COREP forms)
- Regulatory updates monitoring
- Audit logging and user authentication
- Integration with bank systems
- Regulatory approval

## Future Enhancements

1. **Expand Coverage**: Add more COREP templates (CA1, CCR1, etc.)
2. **Full Rulebook**: Index complete PRA Rulebook + EBA guidelines
3. **Advanced RAG**: Implement hybrid search (semantic + keyword)
4. **Fine-tuning**: Fine-tune LLM on regulatory reporting tasks
5. **Validation**: Add complex cross-field validation rules
6. **Multi-Bank**: Support group consolidation
7. **API**: REST API for system integration

## Success Criteria Met

 **End-to-end workflow**: Query → Retrieval → LLM → Template → Export  
 **RAG implementation**: Semantic search over regulatory text  
 **Structured outputs**: JSON schema validation with Pydantic  
 **Template population**: Excel COREP CR1 extract  
 **Validation**: Basic consistency checks  
 **Audit trail**: Regulatory citations for each field  

## License
Prototype for demonstration purposes only.

## Author
Parva - VIT 2026