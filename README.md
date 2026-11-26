# FMT@Fingertips 🩺
### AI-Powered Forensic Medicine and Toxicology Learning Assistant

FMT@Fingertips is an AI-powered educational platform designed to help medical students study Forensic Medicine and Toxicology (FMT). It combines a textbook-oriented knowledge base with a Retrieval-Augmented Generation (RAG) pipeline to deliver structured, context-aware academic explanations.

The platform supports undergraduate (UG/MBBS) and postgraduate (PG) learning modes, with an interface designed for interactive learning, revision and examination preparation.

**Live Application:** https://fmt-fingertips.vercel.app  
**Source Code:** https://github.com/Sahilbarwal/-FMT-Fingertips

---

## 1. Problem Statement

Medical students often need to consult multiple textbooks and learning resources to understand complex forensic medicine topics and prepare for university examinations, practical assessments and viva examinations.

FMT@Fingertips aims to make this learning process more accessible through an interactive assistant that retrieves relevant material from a curated FMT knowledge base and uses it to generate structured explanations.

## 2. Key Features

- **Textbook-oriented AI assistance:** Generates answers using relevant material retrieved from the FMT knowledge base.
- **Retrieval-Augmented Generation:** Combines document retrieval with language-model-based answer generation.
- **UG and PG learning modes:** Adapts the answer structure and level of explanation to the selected academic level.
- **Structured academic responses:** Supports definitions, classifications, mechanisms, comparisons, revision notes and practical/viva preparation.
- **Streaming chat interface:** Displays generated responses through a streaming chat experience.
- **User authentication:** Includes registration, login and JWT-based authentication.
- **Conversation history:** Allows authenticated users to revisit previous questions.
- **User profiles:** Provides account information and profile management.
- **Responsive interface:** Includes light and dark themes and layouts designed for different screen sizes.

## 3. System Architecture

The application follows a frontend-backend architecture with a separate retrieval and answer-generation pipeline.

```text
                   Student
                      |
                      v
              React Frontend
                      |
                      v
               Django Backend
                      |
           +----------+----------+
           |          |          |
           v          v          v
       Accounts    History    RAG Engine
                                  |
                                  v
                         ChromaDB Retriever
                                  |
                                  v
                         Relevant FMT Chunks
                                  |
                                  v
                           Context Builder
                                  |
                                  v
                         Academic Prompting
                                  |
                                  v
                            OpenAI API
                                  |
                                  v
                         Generated Answer
                                  |
                                  v
                         Streaming Response
                                  |
                                  v
                          React Chat UI
```

## 4. Retrieval-Augmented Generation Pipeline

The core AI functionality is implemented in the backend's `rag` module.

### Step 1: Document Ingestion

The ingestion pipeline processes PDF-based learning material.

The standard ingestion process includes:
- Extracting text from PDF documents using PyPDF.
- Cleaning extracted text.
- Splitting the content into smaller overlapping chunks.
- Storing the chunks and associated metadata in a persistent ChromaDB collection.

**Chunk configuration:**
- Chunk size: 1,500 characters
- Chunk overlap: 250 characters
- ChromaDB collection: `fmt_knowledge_base`

### Step 2: Context Retrieval

When a student submits a question:
- The retriever queries the ChromaDB collection.
- It initially retrieves a candidate set of relevant chunks.
- Source metadata and chunk information are retained.
- Selection rules limit repeated material from the same PDF and avoid immediately adjacent chunks.
- The selected content is passed to the answer-generation module.

### Step 3: Context Construction

Retrieved content is organised with source names, chunk identifiers and extracted text before being supplied to the language model.

### Step 4: Academic Answer Generation

The RAG engine constructs a level-specific prompt and sends the question together with the retrieved context to the OpenAI API.

The prompting system distinguishes between undergraduate and postgraduate learning requirements and adapts the depth and organisation of the response.

### Step 5: Response Delivery

The generated answer is returned to the frontend through the chat API. The streaming interface renders the response using Markdown formatting.

## 5. PDF and OCR Processing

The project includes two document-processing paths:

**Standard PDF ingestion**
- Uses PyPDF for text extraction.
- Cleans extracted text.
- Creates overlapping chunks.
- Stores document content and metadata in ChromaDB.

**OCR-based ingestion utility**
- Uses PyMuPDF to render PDF pages.
- Uses Tesseract OCR to extract text from scanned pages.
- Applies text cleaning and chunking before adding extracted content to ChromaDB.
- Uses batch insertion for processing larger document collections.

The OCR utility is maintained separately from the standard ingestion script.

## 6. Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React.js, Vite, JavaScript |
| UI and Markdown | CSS, Lucide React, React Markdown |
| Backend | Python, Django, Django REST Framework |
| Authentication | JWT, Simple JWT |
| AI Integration | OpenAI API |
| RAG | Retrieval-Augmented Generation |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| OCR Processing | Tesseract, PyMuPDF, Pillow |
| HTTP Client | Axios |
| Deployment | Vercel, Render |

## 7. Backend API Endpoints

The backend exposes endpoints for authentication, user management, conversation history and AI interactions.

| Endpoint | Purpose |
|---|---|
| `POST /register/` | User registration |
| `POST /login/` | User login |
| `POST /logout/` | User logout |
| `GET /me/` | Retrieve user profile |
| `GET /history/` | Retrieve conversation history |
| `DELETE /history/` | Clear conversation history |
| `POST /ask/` | Submit an FMT question |
| `POST /ask/stream/` | Submit a question through the streaming interface |
| `POST /token/refresh/` | Refresh an authentication token |

Protected endpoints require an appropriate bearer access token.

## 8. Local Development Setup

### Prerequisites

- Python
- Node.js and npm
- Git
- An OpenAI API key

### Clone the repository

```bash
git clone https://github.com/Sahilbarwal/-FMT-Fingertips.git
cd -FMT-Fingertips
```

### Backend setup

```bash
cd backend

python -m venv venv
```

Activate the virtual environment.

Windows:

```powershell
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment variables in `backend/.env` using the project's environment template.

At minimum, configure the OpenAI API key and the other settings required by the backend configuration.

Run database migrations:

```bash
python manage.py migrate
```

Start the backend:

```bash
python manage.py runserver
```

### Frontend setup

Open another terminal:

```bash
cd frontend

npm install
npm run dev
```

Configure the frontend API URL to point to your local Django backend when running locally.

## 9. Environment Configuration

Keep credentials and deployment-specific settings outside the source code.

The backend uses environment-based configuration, including:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_configured_model
```

Do not commit API keys, database credentials, access tokens or private configuration files to GitHub.

## 10. Deployment

The project uses a separately deployed frontend and backend:

- Frontend: Vercel
- Backend: Render
- AI services: OpenAI API
- Vector retrieval: ChromaDB

The frontend communicates with the backend through HTTP API endpoints.

## 11. Limitations and Future Improvements

Potential areas for further development include:

- Improved retrieval evaluation and relevance measurement.
- More comprehensive automated testing.
- Stronger source-level references in generated answers.
- Enhanced document processing and OCR deployment support.
- Performance optimisation and caching.
- Improved monitoring, logging and error handling.
- More robust evaluation of factual accuracy and hallucination risks.

## 12. Screenshots

Add application screenshots here to demonstrate:

- Home page
- UG/PG selection
- Chat interface
- Generated academic responses
- Conversation history
- User profile

---

**FMT@Fingertips — Making Forensic Medicine learning more structured, accessible and interactive.**
