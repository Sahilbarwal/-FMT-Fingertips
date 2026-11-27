# FMT@Fingertips — Frontend

**A React-based web application for an AI-powered Forensic Medicine and Toxicology (FMT) learning assistant.**

FMT@Fingertips provides an interactive learning platform for undergraduate and postgraduate medical students. It allows users to ask subject-related questions, explore concepts through AI-generated explanations, and revisit previous learning sessions.

The frontend is built using React and Vite and communicates with a Django REST Framework backend for authentication, conversation history, and AI-powered responses.

**Live Application:** https://fmt-fingertips.vercel.app

**Main Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips

**Backend:** Django REST Framework

---

## 1. Application Overview

FMT@Fingertips is designed to make Forensic Medicine and Toxicology learning more accessible through an AI-powered conversational interface.

The application supports two learning levels:

- **Undergraduate (UG):** Exam-oriented explanations designed for undergraduate medical students.
- **Postgraduate (PG):** Advanced and detailed explanations for postgraduate medical learning.

Users can interact with the learning assistant, manage their accounts, and access previously saved questions and conversations.

## 2. Application Screenshots

The following screenshots showcase the frontend interface and its major functionalities.

### 2.1 Login Page

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20051229.png" width="750" alt="FMT@Fingertips Login Page">
</p>

The login interface allows registered users to securely access their accounts using email and password credentials.

### 2.2 Home Page – Learning Level Selection

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113327.png" width="900" alt="FMT@Fingertips Home Page">
</p>

The home page provides an overview of the learning assistant and allows users to choose between Undergraduate (UG) and Postgraduate (PG) learning modes.

### 2.3 AI-Powered Chat Interface

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113518.png" width="900" alt="FMT@Fingertips AI Chat Interface">
</p>

The chat interface is the primary learning environment, where users submit Forensic Medicine questions and receive structured AI-generated responses.

Features include:
- Interactive conversational interface.
- Streaming AI-generated responses.
- Markdown-based answer rendering.
- UG and PG learning modes.
- Recent conversation navigation.
- New study session functionality.

### 2.4 Search History

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113533.png" width="900" alt="FMT@Fingertips Search History">
</p>

The search history page allows users to revisit previous questions and conversations.

Features include:
- View previously saved questions.
- Search through previous queries.
- Open previous conversations.
- Clear search history.

### 2.5 User Profile

<p align="center">
  <img src="FMT_Frontend_Outputs/Screenshot%202026-11-27%20113602.png" width="900" alt="FMT@Fingertips User Profile">
</p>

The profile page displays account information and provides quick access to search history and logout functionality.

---

## 3. Key Features

### User Authentication
- User registration and login.
- Email-based authentication.
- JWT access and refresh token handling.
- Protected routes for authenticated users.
- Logout functionality.

### Learning Level Selection
- Undergraduate (UG) learning mode.
- Postgraduate (PG) learning mode.
- Different learning experiences based on the selected academic level.

### AI-Powered Chat Interface
- Ask questions related to Forensic Medicine and Toxicology.
- Receive AI-generated explanations.
- Streaming response interface.
- Structured answer presentation using Markdown.
- New study session functionality.
- Recent conversation navigation.

### Search History
- Retrieve previously saved questions.
- Search previous queries.
- Revisit earlier learning sessions.
- Clear personal search history.

### User Profile
- Display account information.
- Access personal search history.
- Logout functionality.

### User Interface
- Responsive web interface.
- Light and dark theme support.
- Sidebar navigation.
- Interactive components and icons.
- Markdown rendering with GitHub Flavored Markdown support.

---

## 4. Technology Stack

| Category | Technology |
|---|---|
| Frontend Framework | React 19 |
| Build Tool | Vite |
| Programming Language | JavaScript (ES Modules) |
| Routing | React Router DOM |
| HTTP Client | Axios |
| Markdown Rendering | React Markdown |
| Markdown Extensions | Remark GFM |
| Icons | Lucide React, React Icons |
| Styling | CSS |
| Authentication | JWT |
| Browser Storage | Local Storage |
| Code Linting | Oxlint |
| Deployment | Vercel |

---

## 5. Project Structure

The frontend follows a modular component-based architecture.

```text
frontend/
│
├── public/
│
├── FMT_Frontend_Outputs/
│   ├── Screenshot 2026-11-27 051229.png
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

## 6. Application Routing

The application uses React Router DOM for navigation and route protection.

| Route | Page | Access |
|---|---|---|
| `/login` | Login | Public |
| `/register` | Registration | Public |
| `/` | Home | Protected |
| `/chat` | Chat | Protected |
| `/history` | Search History | Protected |
| `/profile` | Profile | Protected |

Protected routes are handled through the `ProtectedRoute` component to restrict access to authenticated users.

---

## 7. Backend Integration

The frontend communicates with a separate Django REST Framework backend through HTTP requests.

**Production Backend:**

`https://fmt-fingertips-backend.onrender.com`

### API Endpoints

| Endpoint | Method | Functionality |
|---|---|---|
| `/register/` | POST | Register a new user |
| `/login/` | POST | Authenticate a user |
| `/me/` | GET | Retrieve user profile |
| `/history/` | GET | Retrieve search history |
| `/history/` | DELETE | Clear search history |
| `/ask/stream/` | POST | Stream AI-generated responses |

Authenticated requests include the JWT access token in the Authorization header.

```http
Authorization: Bearer <access-token>
```

The frontend and backend are deployed independently, with the frontend hosted on Vercel and the backend hosted on Render.

---

## 8. Authentication and Data Handling

The frontend implements JWT-based authentication to manage user sessions.

Key implementation details:

- Access and refresh tokens are handled by the authentication layer.
- Authentication information is stored in browser Local Storage.
- Protected routes restrict access to authenticated users.
- User profile and search history are retrieved through backend API endpoints.
- Recent chat information is maintained in browser storage for conversation navigation.

---

## 9. Getting Started

### Prerequisites

- Node.js
- npm
- Git
- Code editor such as Visual Studio Code

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

The Vite development server will provide a local URL, typically:

`http://localhost:5173`

### Build for Production

```bash
npm run build
```

---

## 10. Deployment

The frontend is deployed using Vercel.

**Live Application:** https://fmt-fingertips.vercel.app

The production frontend communicates with the deployed Django REST Framework backend.

---

## 11. Future Enhancements

- Improve conversational context management.
- Enhance the learning experience for UG and PG students.
- Improve mobile responsiveness.
- Expand chat search and conversation management.
- Enhance error handling and loading states.
- Introduce additional interactive learning and revision features.

---

## 12. Project Links

**Live Application:** https://fmt-fingertips.vercel.app

**GitHub Repository:** https://github.com/Sahilbarwal/-FMT-Fingertips

**Backend:** Django REST Framework

---

*FMT@Fingertips – Your Forensic Medicine Assistant at Your Fingertips.*
