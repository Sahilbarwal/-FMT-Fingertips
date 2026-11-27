# FMT@Fingertips – Frontend

**A React-based frontend for an AI-powered Forensic Medicine and Toxicology (FMT) learning assistant.**

FMT@Fingertips is a web-based learning platform designed for undergraduate and postgraduate medical students. The frontend provides an interactive interface for asking FMT-related questions, exploring AI-generated explanations, managing study sessions, and accessing personal learning history.

Built using **React 19 and Vite**, the frontend focuses on component-based development, client-side routing, authentication state management, API integration, and responsive user experience.

**Live Application:** https://fmt-fingertips.vercel.app

**GitHub Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips

---

## 1. Frontend Overview

The frontend serves as the primary user interface of FMT@Fingertips, connecting students with the application's AI-powered learning functionality.

It provides:

- A dedicated interface for UG and PG learning modes.
- An interactive conversational interface.
- User registration and login screens.
- Protected navigation for authenticated users.
- Personal search history and conversation navigation.
- User profile management.
- Light and dark theme support.

The frontend communicates with a separately deployed Django REST Framework backend through HTTP API requests.

## 2. Application Screenshots

### 2.1 Login Interface

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20051229.png" width="750" alt="FMT@Fingertips Login Interface">
</p>

A clean authentication interface that allows users to sign in using their registered email and password.

### 2.2 Home Page and Learning Mode Selection

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113327.png" width="950" alt="FMT@Fingertips Home Page">
</p>

The home page introduces the learning assistant and provides separate learning modes:

- **UG Mode:** Exam-oriented explanations for undergraduate medical students.
- **PG Mode:** More advanced and detailed explanations for postgraduate medical students.

### 2.3 AI Chat Interface

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113518.png" width="950" alt="FMT@Fingertips Chat Interface">
</p>

The primary interaction interface, allowing users to submit questions and view AI-generated answers.

Frontend functionality includes:
- Dynamic chat interface.
- Streaming response presentation.
- Markdown-based answer rendering.
- Conversation navigation through the sidebar.
- New study session controls.
- Learning-mode selection.
- Interactive message input.

### 2.4 Search History Interface

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113533.png" width="950" alt="FMT@Fingertips Search History">
</p>

A dedicated page for accessing previously submitted questions and conversations.

Features:
- Display previously saved questions.
- Search and filter previous queries.
- Navigate back to previous learning sessions.
- Clear search history.

### 2.5 User Profile Interface

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113602.png" width="950" alt="FMT@Fingertips User Profile">
</p>

The profile interface displays account information and provides quick access to search history and logout functionality.

### 2.6 Frontend Production Deployment

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20111130.png" width="950" alt="FMT@Fingertips Vercel Deployment">
</p>

The frontend is deployed through Vercel and connected to the GitHub repository for production deployments.

---

## 3. Frontend Features and Implementation

### 3.1 Component-Based Architecture

The application follows a modular React architecture.

Reusable components are used to separate interface elements and simplify maintenance.

Examples include:
- `ChatBox.jsx` – Chat interface.
- `InputBox.jsx` – User question input.
- `Message.jsx` – Message rendering.
- `Sidebar.jsx` – Navigation and recent conversations.
- `Navbar.jsx` – Application navigation.
- `Loading.jsx` – Loading interface.
- `SearchHistory.jsx` – Search history components.

### 3.2 State Management

React Context API is used to manage shared application state.

The frontend contains separate context modules:

- **AuthContext:** Manages authentication-related state.
- **ChatContext:** Manages chat and conversation-related state.
- **ThemeContext:** Manages light and dark theme preferences.

This separation helps keep application state organised across different pages and components.

### 3.3 Client-Side Routing

React Router DOM handles navigation between application pages.

The `ProtectedRoute` component restricts access to authenticated sections.

| Route | Component | Access |
|---|---|---|
| `/login` | Login | Public |
| `/register` | Register | Public |
| `/` | Home | Protected |
| `/chat` | Chat | Protected |
| `/history` | History | Protected |
| `/profile` | Profile | Protected |

### 3.4 Authentication Handling

The frontend integrates with the backend authentication API.

Implemented functionality includes:
- User registration and login forms.
- Email and password input handling.
- JWT access and refresh token handling.
- Authentication state management.
- Protected route navigation.
- Logout functionality.
- Browser Local Storage for authentication information.

### 3.5 API Integration

Axios is used for communicating with the backend.

The API service module centralises HTTP communication between the frontend and backend.

**Production Backend URL:**

`https://fmt-fingertips-backend.onrender.com`

| API Endpoint | Method | Frontend Purpose |
|---|---|---|
| `/register/` | POST | Submit registration details |
| `/login/` | POST | Authenticate users |
| `/me/` | GET | Retrieve profile information |
| `/history/` | GET | Retrieve search history |
| `/history/` | DELETE | Clear search history |
| `/ask/stream/` | POST | Submit questions and receive streamed responses |

Authenticated requests include the JWT access token in the Authorization header.

### 3.6 Dynamic Chat Rendering

The chat interface supports:
- Dynamic rendering of user and assistant messages.
- Streaming response presentation.
- Markdown-formatted content.
- GitHub Flavored Markdown through Remark GFM.
- Conversation navigation.
- Recent chat information stored in browser Local Storage.

### 3.7 UI and Theme Management

The frontend provides:
- Light and dark theme support.
- Responsive page layouts.
- Sidebar-based navigation.
- Reusable interface elements.
- Interactive icons using Lucide React and React Icons.
- Structured Markdown content presentation.

---

## 4. Technology Stack

| Category | Technology |
|---|---|
| Frontend Framework | React 19 |
| Build Tool | Vite |
| Programming Language | JavaScript (ES Modules) |
| Routing | React Router DOM |
| State Management | React Context API |
| HTTP Client | Axios |
| Markdown Rendering | React Markdown |
| Markdown Extensions | Remark GFM |
| Icons | Lucide React, React Icons |
| Styling | CSS |
| Authentication Handling | JWT |
| Browser Storage | Local Storage |
| Code Linting | Oxlint |
| Deployment | Vercel |
| Version Control | Git and GitHub |

---

## 5. Frontend Project Structure

The frontend follows a modular, component-based folder structure.

```text
frontend/
│
├── public/
│
├── FMT_Frontend_Outputs/
│   ├── Screenshot 2026-11-27 051229.png
│   ├── Screenshot 2026-11-27 111130.png
│   ├── Screenshot 2026-11-27 113327.png
│   ├── Screenshot 2026-11-27 113518.png
│   ├── Screenshot 2026-11-27 113533.png
│   └── Screenshot 2026-11-27 113602.png
│
├── src/
│   │
│   ├── assets/
│   │
│   ├── components/
│   │   ├── ChatBox.jsx
│   │   ├── InputBox.jsx
│   │   ├── Loading.jsx
│   │   ├── Message.jsx
│   │   ├── Navbar.jsx
│   │   ├── SearchHistory.jsx
│   │   └── Sidebar.jsx
│   │
│   ├── context/
│   │   ├── AuthContext.jsx
│   │   ├── ChatContext.jsx
│   │   └── ThemeContext.jsx
│   │
│   ├── pages/
│   │   ├── Chat.jsx
│   │   ├── History.jsx
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Profile.jsx
│   │   └── Register.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── styles/
│   │
│   ├── App.jsx
│   ├── App.css
│   ├── Home.css
│   ├── index.css
│   ├── main.jsx
│   └── ProtectedRoute.jsx
│
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

---

## 6. Frontend and Backend Communication

The frontend and backend are maintained as separate application layers.

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React + Vite | User interface and client-side interactions |
| API Communication | Axios | HTTP requests and responses |
| Authentication | JWT | Client-side token handling |
| Backend | Django REST Framework | API processing and application logic |
| Deployment | Vercel | Frontend hosting |

The frontend handles the presentation and interaction layer, while backend services process authentication, search history, and AI-generated responses.

---

## 7. Local Development Setup

### Prerequisites

- Node.js
- npm
- Git
- Visual Studio Code or another code editor

### Clone the Repository

```bash
git clone https://github.com/Sahilbarwal/-FMT-Fingertips.git
```

### Navigate to the Frontend Directory

```bash
cd -FMT-Fingertips/frontend
```

### Install Dependencies

```bash
npm install
```

### Start the Development Server

```bash
npm run dev
```

The application will be available at:

`http://localhost:5173`

### Create a Production Build

```bash
npm run build
```

---

## 8. Deployment

The frontend is deployed on **Vercel** and connected to the GitHub repository.

**Production URL:** https://fmt-fingertips.vercel.app

The deployment workflow allows updated frontend code pushed to the configured GitHub branch to be deployed through Vercel.

---

## 9. Future Improvements

- Improve responsive layouts across mobile and tablet devices.
- Enhance chat interface interactions.
- Improve conversation search and navigation.
- Refine loading and error states.
- Improve accessibility and UI consistency.
- Introduce additional interactive learning components.

---

## 10. Project Links

- **Live Frontend:** https://fmt-fingertips.vercel.app
- **GitHub Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips
- **Backend Service:** Django REST Framework

---

*FMT@Fingertips – Your Forensic Medicine Assistant at Your Fingertips.*
