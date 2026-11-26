# FMT@Fingertips — Frontend

**React-based web application for an AI-powered Forensic Medicine and Toxicology learning assistant.**

FMT@Fingertips provides a dedicated learning interface for medical students to explore Forensic Medicine and Toxicology (FMT) topics. The frontend connects to a Django REST Framework backend that handles authentication, conversation history, document retrieval and AI-generated responses.

**Live Application:** https://fmt-fingertips.vercel.app  
**Main Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips  
**Backend:** Django REST Framework

---

## Overview

The frontend is built using React and Vite. It provides an interactive interface through which users can:

- Select undergraduate (UG) or postgraduate (PG) learning modes.
- Ask questions related to Forensic Medicine and Toxicology.
- View AI-generated responses through a streaming chat interface.
- Register and log in using an account.
- Access their previous search history.
- View account profile information.
- Switch between light and dark themes.
- Revisit recent conversations stored in the browser.

## Application Pages

### 1. Home Page

The home page acts as the main entry point for authenticated users.

Features:
- UG and PG learning-level selection.
- FMT topic suggestions.
- Question input and navigation to the chat interface.
- Quick access to search history and profile.
- Light and dark theme switching.

### 2. Authentication

The application includes registration and login pages.

**Registration**
- Collects full name, email and password.
- Generates a username from the email address.
- Performs basic password confirmation and length validation.
- Sends registration details to the backend.

**Login**
- Authenticates users using email and password.
- Receives JWT access and refresh tokens.
- Stores authentication information in browser local storage.

### 3. Chat Interface

The chat page is the primary learning interface.

Features:
- UG and PG learning-level selection.
- Question submission to the backend.
- Streaming AI responses.
- Markdown-based answer rendering.
- Structured headings and formatted content.
- Recent chat storage in browser local storage.
- Conversation navigation and chat history controls.
- Responsive sidebar and chat layout.

The main chat interface communicates with the backend's streaming endpoint:

`POST /ask/stream/`

### 4. Search History

The history page retrieves previously saved questions from the backend.

Features:
- Displays saved questions.
- Searches previous questions using a text filter.
- Opens a previous question in the chat interface.
- Clears the user's complete search history after confirmation.

### 5. User Profile

The profile page displays authenticated account information retrieved from the backend.

Features:
- User information.
- Account details.
- Navigation to search history.
- Logout functionality.

---

## Technology Stack

| Category | Technology |
|---|---|
| Frontend framework | React 19 |
| Build tool | Vite |
| Programming language | JavaScript (ES Modules) |
| Routing | React Router DOM |
| HTTP requests | Axios |
| Markdown rendering | React Markdown |
| Markdown extensions | Remark GFM |
| Icons | Lucide React, React Icons |
| Styling | CSS |
| Authentication | JWT-based authentication |
| Browser storage | Local Storage |
| Code linting | Oxlint |
| Deployment | Vercel |

---

## Project Structure

```text
frontend/
│
├── public/
│
├── src/
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

## Application Routing

The application uses React Router DOM.

| Route | Page | Access |
|---|---|---|
| `/login` | Login | Public |
| `/register` | Registration | Public |
| `/` | Home | Protected |
| `/chat` | Chat | Protected |
| `/history` | Search History | Protected |
| `/profile` | Profile | Protected |

Protected routes are wrapped using the `ProtectedRoute` component.

Unknown routes redirect users to the home route.

---

## Backend Integration

The frontend communicates with the Django backend through HTTP requests.

**Production backend base URL:**

`https://fmt-fingertips-backend.onrender.com`

| Endpoint | Method | Frontend functionality |
|---|---|---|
| `/register/` | POST | Account registration |
| `/login/` | POST | User authentication |
| `/me/` | GET | Retrieve profile information |
| `/history/` | GET | Retrieve search history |
| `/history/` | DELETE | Clear search history |
| `/ask/stream/` | POST | Stream AI-generated answers |

Authenticated requests include the JWT access token in the Authorization header:

```http
Authorization: Bearer <access-token>
```

The frontend and backend are deployed separately.

---


## License

**FMT@Fingertips — Your Forensic Medicine Assistant at Your Fingertips.**
