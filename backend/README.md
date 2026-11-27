# FMT@Fingertips – Backend

**Django REST Framework backend for an AI-powered Forensic Medicine and Toxicology (FMT) learning assistant.**

The backend powers FMT@Fingertips by connecting the React frontend with an AI-based question-answering system. It handles user authentication, API communication, knowledge retrieval and AI-generated responses.

The application uses a Retrieval-Augmented Generation (RAG) architecture, combining a dedicated FMT knowledge base, ChromaDB vector retrieval and the OpenAI API to generate contextual learning responses.

**Live Application:** https://fmt-fingertips.vercel.app

**Backend API:** https://fmt-fingertips-backend.onrender.com

**GitHub Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips

---

## 1. Backend Overview

The backend is developed using Python, Django and Django REST Framework.

Its primary responsibility is to process questions submitted by authenticated users, retrieve relevant information from the FMT knowledge base and generate structured responses using an OpenAI model.

### Core Responsibilities

- User registration and authentication.
- JWT-based API authentication.
- REST API development and frontend integration.
- Processing Forensic Medicine and Toxicology questions.
- Retrieval of relevant information from ChromaDB.
- AI response generation using the OpenAI API.
- Support for Undergraduate (UG) and Postgraduate (PG) learning levels.
- Search history management.
- Structured Markdown response delivery.

## 2. Backend Architecture

FMT@Fingertips follows a Retrieval-Augmented Generation (RAG) architecture.

Instead of relying exclusively on the language model's general knowledge, the system retrieves relevant information from a dedicated FMT knowledge base and uses the retrieved context to generate answers.

### RAG Workflow

1. The user submits an FMT-related question through the React frontend.
2. Django REST Framework receives the authenticated API request.
3. The RAG engine processes the question.
4. ChromaDB retrieves relevant information from the FMT vector database.
5. The retrieved context is passed to the OpenAI model.
6. The model generates a contextual response.
7. Django returns the generated answer to the frontend.
8. The frontend renders the answer in a structured Markdown format.

### Architecture Diagram

```text
                 React Frontend
                       |
                       v
              Django REST Framework
                       |
                       v
                 User Question
                       |
                       v
                  RAG Engine
                       |
                       v
              ChromaDB Retrieval
                       |
                       v
                Relevant Context
                       |
                       v
                  OpenAI API
                       |
                       v
               Generated FMT Answer
                       |
                       v
               Django REST API
                       |
                       v
                 React Frontend
```

**Architecture Note:** This is a custom RAG-based implementation, not a direct Custom GPT connection. It combines a dedicated web application, backend services, a subject-specific knowledge base and an OpenAI model.

## 3. Technology Stack

| Category | Technology |
|---|---|
| Backend Framework | Django |
| API Framework | Django REST Framework |
| Programming Language | Python |
| AI Integration | OpenAI API |
| Architecture | Retrieval-Augmented Generation (RAG) |
| Vector Database | ChromaDB |
| Authentication | JWT |
| Object Storage | Cloudflare R2 |
| Database Infrastructure | Supabase project |
| Deployment | Render |
| Configuration | Environment Variables |

*The Supabase dashboard is included as an infrastructure reference; its presence alone does not establish that it is the active Django database.*

## 4. Infrastructure and Deployment

The backend uses separate infrastructure services for application hosting and knowledge-base storage.

### 4.1 Backend Hosting – Render

The Django backend is deployed on Render.

![Render Backend Deployment](FMT_Backend_Websites/Screenshot%202026-11-27%20111159.png)

The deployment hosts the backend application and exposes API endpoints consumed by the React frontend.

**Production Backend URL:**

https://fmt-fingertips-backend.onrender.com

### 4.2 Knowledge Base Object Storage – Cloudflare R2

![Cloudflare R2 Dashboard](FMT_Backend_Websites/Screenshot%202026-11-27%20111140.png)

Cloudflare R2 is used for object storage associated with the FMT knowledge base.

The configured bucket shown in the dashboard is named `fmt-knowledge-base`.

### 4.3 Database Infrastructure – Supabase

![Supabase Dashboard](FMT_Backend_Websites/Screenshot%202026-11-27%20113018.png)

The Supabase dashboard provides an overview of the FMT-Fingertips database project, including its infrastructure status and usage metrics.

## 5. Backend Project Structure

The backend follows a modular Django project structure.

```text
backend/
│
├── accounts/
│   └── User authentication and account management
│
├── config/
│   └── Django project configuration
│
├── rag/
│   ├── documents/
│   │   └── FMT knowledge-base documents
│   │
│   ├── vectorstore/
│   │   └── ChromaDB vector database
│   │
│   ├── retriever.py
│   ├── rag_engine.py
│   └── Other RAG components
│
├── FMT_Backend_Websites/
│   ├── Screenshot 2026-11-27 111140.png
│   ├── Screenshot 2026-11-27 111159.png
│   └── Screenshot 2026-11-27 113018.png
│
├── manage.py
├── requirements.txt
├── README_FIRST.txt
└── README.md
```

*This structure highlights the main backend modules and the infrastructure screenshots. Additional source files and configuration files may exist within the individual directories.*

## 6. API Integration

The backend exposes REST API endpoints consumed by the React frontend.

### AI Question Answering

**Endpoint:**

`POST /ask/`

**Production URL:**

`https://fmt-fingertips-backend.onrender.com/ask/`

**Request Body:**

```json
{
  "question": "What is rigor mortis?",
  "level": "UG"
}
```

**Authentication Header:**

```http
Authorization: Bearer <access-token>
```

The endpoint requires an authenticated user and accepts the question and selected learning level.

The backend processes the request through the RAG pipeline and returns an AI-generated response.

### Frontend Streaming Endpoint

The frontend also uses the streaming question-answering endpoint:

`POST /ask/stream/`

This endpoint supports the streaming response experience in the React chat interface.

### API Capabilities

- User registration and authentication.
- Authenticated question submission.
- AI-generated answer delivery.
- UG and PG learning-level support.
- Search history retrieval and management.
- User profile retrieval.

## 7. Retrieval-Augmented Generation (RAG)

The RAG pipeline is a central component of FMT@Fingertips.

It combines vector-based information retrieval with AI-generated responses to provide answers informed by the application's FMT knowledge base.

### Main Components

**Question Processing**

Receives and processes the user's question.

**Context Retrieval**

Uses ChromaDB to retrieve relevant information from the indexed FMT knowledge base.

**Contextual Generation**

Passes the retrieved information to the OpenAI model.

**Answer Generation**

Generates a structured response based on the question and retrieved context.

**Response Delivery**

Returns the generated answer to the frontend.

### Learning Levels

The backend supports two learning levels:

- **Undergraduate (UG):** Exam-oriented explanations for undergraduate medical students.
- **Postgraduate (PG):** Advanced and detailed explanations for postgraduate medical learning.

## 8. Authentication and Security

The backend supports authenticated API communication between the frontend and backend.

Key implementation areas include:

- User registration and login.
- JWT-based authentication.
- Protected API endpoints.
- Authenticated question submission.
- User-specific search history.
- Environment-based configuration for sensitive credentials.

Sensitive configuration such as OpenAI API keys should be stored in environment variables and must not be committed to GitHub.

## 9. Local Installation and Setup

### Prerequisites

- Python
- pip
- Git
- Virtual environment
- OpenAI API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sahilbarwal/-FMT-Fingertips.git
```

### Step 2: Navigate to the Backend

```bash
cd -FMT-Fingertips/backend
```

### Step 3: Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create a `.env` file from the example configuration:

```powershell
copy .env.example .env
```

Configure the required OpenAI credentials:

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-5.4-nano
```

Never commit actual API keys or private credentials to the repository.

### Step 6: Run Database Migrations

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

The local backend will be available at:

`http://127.0.0.1:8000/`

## 10. Testing the RAG System

### Test ChromaDB Connection

Run the following command to verify the existing ChromaDB collection:

```bash
python -c "from rag.retriever import get_collection; c=get_collection(); print(c.name); print('CHUNKS:',c.count())"
```

### Test AI Answer Generation

```bash
python manage.py shell -c "from rag.rag_engine import generate_answer; r=generate_answer('What is rigor mortis?','UG'); print('ERROR:',r.get('error')); print('MODEL:',r.get('model')); print('TIMING:',r.get('timing')); print(r.get('answer',''))"
```

These commands help verify the vector database connection and AI answer-generation workflow.

## 11. Knowledge Base Preservation

The existing knowledge base contains important document and vector database data.

The following directories must be preserved:

```text
rag/
├── documents/
└── vectorstore/
```

Important instructions:

- Do not delete `rag/documents/`.
- Do not delete `rag/vectorstore/`.
- Reuse the existing ChromaDB vectorstore whenever possible.
- Do not run `rag/ingest.py` unless intentionally rebuilding the entire vector database.

Rebuilding the vector database may replace or modify the existing indexed knowledge base.

## 12. Future Enhancements

- Improve RAG retrieval accuracy.
- Expand the FMT knowledge base.
- Improve contextual conversation handling.
- Enhance response generation for UG and PG learning levels.
- Optimise vector search performance.
- Improve API monitoring and error handling.
- Expand automated backend testing.
- Strengthen authentication and API security.

## 13. Project Links

**Live Application:** https://fmt-fingertips.vercel.app

**Backend API:** https://fmt-fingertips-backend.onrender.com

**GitHub Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips

---

*FMT@Fingertips – A custom RAG-powered learning assistant for Forensic Medicine and Toxicology.*
