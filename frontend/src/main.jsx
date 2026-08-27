import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App.jsx";
import { ThemeProvider } from "./context/ThemeContext.jsx";

import "./styles/global.css";
import "./styles/auth.css";
import "./styles/home.css";
import "./styles/chat.css";
import "./styles/history.css";
import "./styles/profile.css";
import "./styles/theme.css";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);