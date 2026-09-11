# FMT@Fingertips 🩺

### AI-Powered Forensic Medicine Learning Assistant

FMT@Fingertips is an AI-powered learning platform designed to help medical students study **Forensic Medicine and Toxicology (FMT)** through textbook-grounded answers, exam-focused explanations, and an interactive chat experience.

The platform supports both **Undergraduate (UG)** and **Postgraduate (PG)** learning modes and uses a Retrieval-Augmented Generation (RAG) pipeline to provide answers based on curated FMT study material.

---

## ✨ Features

- 🤖 **AI-powered FMT assistant**
- 📚 **Textbook-grounded answers using RAG**
- 🎓 **UG and PG learning modes**
- 📝 **Exam-oriented explanations**
- 💬 **Streaming AI responses**
- 🔐 **JWT-based authentication**
- 👤 **User profiles**
- 🕘 **Search/history management**
- 🌙 **Light and dark mode**
- 📱 **Responsive UI for mobile, tablet and desktop**
- 📎 **Image attachment support**
- 🔎 **Topic-based FMT exploration**
- ☁️ **Production deployment with Vercel + Render**

---

## 🧠 How It Works

```text
                User Question
                     │
                     ▼
              React Frontend
                     │
                     ▼
              Django Backend
                     │
                     ▼
                ChromaDB
             Vector Retrieval
                     │
                     ▼
             Relevant FMT Text
                     │
                     ▼
                  OpenAI
                     │
                     ▼
             Generated Answer
                     │
                     ▼
             Streamed to User
