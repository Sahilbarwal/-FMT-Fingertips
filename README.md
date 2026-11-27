# FMT@Fingertips 🩺
### AI-Powered Forensic Medicine and Toxicology Learning Assistant

**FMT@Fingertips** is an AI-powered educational platform designed to support medical students in learning and revising Forensic Medicine and Toxicology (FMT).

The platform combines a curated, textbook-oriented knowledge base with a Retrieval-Augmented Generation (RAG) pipeline to deliver structured, context-aware academic explanations. It provides separate Undergraduate (UG/MBBS) and Postgraduate (PG) learning modes through an interactive web application.

Built using **React, Django REST Framework, ChromaDB and the OpenAI API**, the application integrates document retrieval, AI-powered answer generation, user authentication and conversation history into a unified learning experience.

<blockquote>
  **Live Application:** https://fmt-fingertips.vercel.app

  **GitHub Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips

  **Frontend:** React + Vite

  **Backend:** Django REST Framework
</blockquote>

---

## 1. Project Overview

Forensic Medicine and Toxicology involves a wide range of medical, scientific and medico-legal concepts. Students often need to consult multiple textbooks and learning resources to understand complex topics and prepare for university examinations, practical assessments and viva examinations.

FMT@Fingertips aims to simplify this learning process through an AI-powered assistant that retrieves relevant information from a dedicated FMT knowledge base and generates structured academic explanations.

The platform is designed to provide:

- Subject-specific learning assistance.
- Context-aware answers based on retrieved knowledge-base content.
- Different explanation levels for undergraduate and postgraduate students.
- Interactive question-answering and revision.
- Personalised access through user accounts and conversation history.

## 2. Problem Statement

General-purpose AI assistants may generate explanations without consistently grounding their responses in a student's prescribed subject material.

For medical education, the relevance, organisation and context of information are particularly important.

FMT@Fingertips addresses this challenge by combining document retrieval with language-model-based answer generation. The system retrieves relevant content from its FMT knowledge base and uses that information as context for generating academic responses.

The goal is to make subject-specific learning more organised, accessible and interactive.

## 3. Key Features

### AI-Powered FMT Learning

- Ask questions related to Forensic Medicine and Toxicology.
- Generate structured academic explanations.
- Retrieve relevant information from the FMT knowledge base.
- Present answers in a readable Markdown format.

### Undergraduate and Postgraduate Learning Modes

- **UG Mode:** Exam-oriented explanations designed for undergraduate medical students.
- **PG Mode:** Advanced and detailed explanations for postgraduate medical learning.
- Learning-level selection through the application interface.

### Retrieval-Augmented Generation

- Document-based knowledge retrieval.
- ChromaDB vector search.
- Context-aware answer generation.
- Integration with the OpenAI API.

### Interactive Chat Interface

- Streaming AI-generated responses.
- New study session functionality.
- Recent conversation navigation.
- Structured Markdown rendering.
- Responsive chat interface.

### User Authentication

- User registration and login.
- JWT-based authentication.
- Protected application routes.
- User profile information.
- Logout functionality.

### Conversation History

- Save and retrieve previous questions.
- Search previously submitted queries.
- Revisit earlier learning sessions.
- Clear personal search history.

### User Interface

- Responsive web interface.
- Light and dark themes.
- Sidebar navigation.
- Interactive components and icons.
- Separate learning-level selection.

---

## 4. Application Screenshots

The following screenshots demonstrate the application's user interface and primary learning workflows.

### 4.1 Login Page

![FMT@Fingertips Login Page](frontend/FMT_Frontend_Outputs/Screenshot%202026-11-27%20051229.png)

The login page allows registered users to access their accounts using their email and password.

### 4.2 Home Page – Learning Level Selection

![FMT@Fingertips Home Page](frontend/FMT_Frontend_Outputs/Screenshot%202026-11-27%20113327.png)

The home page introduces the learning assistant and provides the option to select Undergraduate (UG) or Postgraduate (PG) learning modes.

### 4.3 AI-Powered Chat Interface

![FMT@Fingertips Chat Interface](frontend/FMT_Frontend_Outputs/Screenshot%202026-11-27%20113518.png)

The chat interface allows students to submit FMT questions and receive structured AI-generated explanations. It includes learning-level selection, conversation navigation and a streaming response experience.

### 4.4 Search History

![FMT@Fingertips Search History](frontend/FMT_Frontend_Outputs/Screenshot%202026-11-27%20113533.png)

The search history interface allows authenticated users to search and revisit their previous questions and conversations.

### 4.5 User Profile

![FMT@Fingertips User Profile](frontend/FMT_Frontend_Outputs/Screenshot%202026-11-27%20113602.png)

The profile page displays account information and provides access to personal history and account actions.

---

## 5. System Architecture

FMT@Fingertips follows a frontend-backend architecture with a separate RAG-based retrieval and answer-generation pipeline.

### High-Level Architecture

```text
                    Student
                       |
                       v
                React Frontend
                       |
                       v
              Django REST Framework
                       |
          +------------+-------------+
          |            |             |
          v            v             v
       Accounts     History       RAG Engine
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

### System Components

| Component | Responsibility |
|---|---|
| React Frontend | User interface and interaction |
| Django Backend | API processing and application logic |
| Accounts Module | User registration and authentication |
| History Module | User conversation history |
| RAG Engine | Retrieval and answer-generation workflow |
| ChromaDB | Vector-based knowledge retrieval |
| OpenAI API | Contextual answer generation |

---

## 6. Retrieval-Augmented Generation (RAG) Pipeline

The RAG pipeline is the core AI component of FMT@Fingertips.

It combines a subject-specific knowledge base with an OpenAI language model to generate answers using retrieved contextual information.

### 6.1 Document Ingestion

The document ingestion pipeline processes PDF-based learning material.

The standard ingestion workflow includes:

1. Extracting text from PDF documents using PyPDF.
2. Cleaning extracted text.
3. Splitting the content into smaller overlapping chunks.
4. Storing chunks and associated metadata in a persistent ChromaDB collection.

**Chunk configuration:**

| Parameter | Configuration |
|---|---|
| Chunk size | 1,500 characters |
| Chunk overlap | 250 characters |
| Vector database | ChromaDB |
| Collection | `fmt_knowledge_base` |

### 6.2 Context Retrieval

When a student submits a question:

1. The question is processed by the retriever.
2. ChromaDB retrieves a candidate set of relevant chunks.
3. Source metadata and chunk information are retained.
4. Selection rules limit repeated material from the same PDF and avoid immediately adjacent chunks.
5. Selected content is passed to the answer-generation module.

### 6.3 Context Construction

Retrieved information is organised with source names, chunk identifiers and extracted text before being supplied to the language model.

### 6.4 Academic Answer Generation

The RAG engine constructs a level-specific prompt and sends the question together with the retrieved context to the OpenAI API.

The prompting system distinguishes between undergraduate and postgraduate learning requirements and adapts the depth and organisation of the response.

### 6.5 Response Delivery

The generated answer is returned through the backend API. The frontend renders the response through its streaming chat interface using Markdown formatting.

---

## 7. PDF and OCR Processing

The project includes two document-processing paths.

### Standard PDF Ingestion

- Uses PyPDF for text extraction.
- Cleans extracted content.
- Creates overlapping text chunks.
- Stores document content and metadata in ChromaDB.

### OCR-Based Ingestion Utility

- Uses PyMuPDF to render PDF pages.
- Uses Tesseract OCR to extract text from scanned pages.
- Applies text cleaning and chunking.
- Supports batch insertion into ChromaDB.

The OCR utility is maintained separately from the standard ingestion script.

---

## 8. Technology Stack

| Category | Technologies |
|---|---|
| Frontend Framework | React 19 |
| Frontend Build Tool | Vite |
| Programming Language | JavaScript, Python |
| UI Styling | CSS |
| Routing | React Router DOM |
| HTTP Client | Axios |
| Markdown Rendering | React Markdown, Remark GFM |
| Icons | Lucide React, React Icons |
| Backend Framework | Django |
| REST API | Django REST Framework |
| Authentication | JWT, Simple JWT |
| AI Integration | OpenAI API |
| AI Architecture | Retrieval-Augmented Generation |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| OCR Processing | Tesseract, PyMuPDF, Pillow |
| Object Storage | Cloudflare R2 |
| Frontend Deployment | Vercel |
| Backend Deployment | Render |

---

## 9. Project Structure

The repository is organised into separate frontend and backend applications.

```text
-FMT-Fingertips/
│
├── backend/
│   │
│   ├── accounts/
│   │   └── User authentication and account management
│   │
│   ├── config/
│   │   └── Django project configuration
│   │
│   ├── rag/
│   │   ├── documents/
│   │   │   └── FMT knowledge-base documents
│   │   │
│   │   ├── vectorstore/
│   │   │   └── ChromaDB vector database
│   │   │
│   │   ├── retriever.py
│   │   ├── rag_engine.py
│   │   └── Other RAG components
│   │
│   ├── FMT_Backend_Websites/
│   │   └── Backend infrastructure screenshots
│   │
│   ├── manage.py
│   ├── requirements.txt
│   ├── README.md
│   └── README_FIRST.txt
│
├── frontend/
│   │
│   ├── public/
│   │
│   ├── FMT_Frontend_Outputs/
│   │   └── Frontend application screenshots
│   │
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   │
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── ProtectedRoute.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
└── README.md
```

*The structure above presents the main application modules; individual directories may contain additional files.*

---

## 10. Backend API Integration

The React frontend communicates with the Django REST Framework backend through HTTP requests.

### API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/register/` | POST | User registration |
| `/login/` | POST | User authentication |
| `/logout/` | POST | User logout |
| `/me/` | GET | Retrieve user profile |
| `/history/` | GET | Retrieve conversation history |
| `/history/` | DELETE | Clear conversation history |
| `/ask/` | POST | Submit an FMT question |
| `/ask/stream/` | POST | Stream AI-generated responses |
| `/token/refresh/` | POST | Refresh authentication token |

### Example Question Request

```json
{
  "question": "What is rigor mortis?",
  "level": "UG"
}
```

### Authentication

Protected API requests use a JWT bearer access token.

```http
Authorization: Bearer <access-token>
```

The frontend handles authentication state and communicates with the backend using its API service layer.

---

## 11. Authentication and Data Management

The application implements JWT-based authentication for user access.

Key functionality includes:

- Registration and login.
- Access and refresh token handling.
- Protected frontend routes.
- Authenticated API requests.
- User profile retrieval.
- User-specific search history.
- Browser Local Storage for authentication and recent conversation information.

The backend is responsible for processing authenticated requests and managing the associated account and history data.

---

## 12. Deployment Architecture

The frontend and backend are deployed independently.

| Component | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |
| AI Answer Generation | OpenAI API |
| Vector Retrieval | ChromaDB |
| Object Storage | Cloudflare R2 |

### Deployment Flow

```text
                 User Browser
                      |
                      v
               Vercel Frontend
                      |
                HTTPS Requests
                      |
                      v
               Render Backend
                      |
              +-------+-------+
              |               |
              v               v
          ChromaDB         OpenAI API
              |               |
              +-------+-------+
                      |
                      v
               Generated Answer
                      |
                      v
               React Frontend
```

The frontend communicates with the deployed backend through HTTP API endpoints.

---

## 13. Local Development Setup

### Prerequisites

- Python
- Node.js and npm
- Git
- OpenAI API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sahilbarwal/-FMT-Fingertips.git
cd -FMT-Fingertips
```

### Step 2: Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables in `backend/.env`, using the project's environment template.

Example:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_configured_model
```

Run migrations:

```bash
python manage.py migrate
```

Start the Django server:

```bash
python manage.py runserver
```

The local backend will be available at:

`http://127.0.0.1:8000/`

### Step 3: Frontend Setup

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will typically be available at:

`http://localhost:5173/`

Configure the frontend API URL to point to the local Django backend when running locally.

---

## 14. Knowledge Base Preservation

The existing FMT knowledge base contains important document and vector database data.

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
- Do not run `rag/ingest.py` unless intentionally rebuilding the vector database.

Rebuilding the vector database may replace or modify the existing indexed knowledge base.

---

## 15. Limitations and Future Improvements

Potential areas for further development include:

- Improving retrieval accuracy and relevance evaluation.
- Adding more comprehensive automated testing.
- Improving source-level references in generated answers.
- Expanding the FMT knowledge base.
- Enhancing scanned-document OCR processing.
- Improving contextual conversation management.
- Optimising vector search and response performance.
- Improving monitoring, logging and error handling.
- Strengthening security and deployment reliability.
- Evaluating factual accuracy and reducing hallucination risks.

---

## 16. Project Documentation

For detailed implementation and setup information, refer to the individual project documentation.

- **[Frontend Documentation](frontend/README.md)** – React application, components, pages, state management and frontend setup.
- **[Backend Documentation](backend/README.md)** – Django APIs, authentication, RAG architecture, ChromaDB and backend setup.
- **[Backend Setup Notes](backend/README_FIRST.txt)** – Additional backend installation, testing and knowledge-base preservation instructions.

---

## 17. Project Links

| Resource | Link |
|---|---|
| Live Application | [FMT@Fingertips](https://fmt-fingertips.vercel.app) |
| GitHub Repository | [Source Code](https://github.com/Sahilbarwal/-FMT-Fingertips) |
| Frontend Deployment | [Vercel](https://fmt-fingertips.vercel.app) |
| Backend Deployment | [Render](https://fmt-fingertips-backend.onrender.com) |

---

### FMT@Fingertips

*Making Forensic Medicine learning more structured, accessible and interactive.*

