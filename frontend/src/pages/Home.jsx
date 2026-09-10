import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import "../styles/home.css";

import {
  FaSearch,
  FaBookMedical,
  FaBalanceScale,
  FaSkullCrossbones,
  FaMicroscope,
  FaArrowRight,
  FaHistory,
  FaUserCircle,
  FaGraduationCap,
  FaCheck,
  FaMoon,
  FaSun,
} from "react-icons/fa";

function Home() {
  const navigate = useNavigate();

  const { darkMode, toggleTheme } = useTheme();

  const [level, setLevel] = useState("UG");

  // =====================================================
  // SEARCH
  // =====================================================

  const handleSearch = (event) => {
    event.preventDefault();

    const question = event.target.question.value.trim();

    if (!question) return;

    navigate("/chat", {
      state: {
        question,
        level,
        fromHome: true,
      },
    });
  };

  // =====================================================
  // TOPIC SUGGESTIONS
  // =====================================================

  const suggestions = [
    {
      icon: <FaSkullCrossbones />,
      title: "Poisoning",
      text: "Explore toxicology and poisoning",
    },
    {
      icon: <FaBalanceScale />,
      title: "Medico-Legal",
      text: "Learn important legal aspects",
    },
    {
      icon: <FaMicroscope />,
      title: "Forensic Pathology",
      text: "Study death and autopsy topics",
    },
    {
      icon: <FaBookMedical />,
      title: "General FMT",
      text: "Ask about any FMT topic",
    },
  ];

  // =====================================================
  // OPEN TOPIC
  // =====================================================

  const openTopic = (title) => {
    navigate("/chat", {
      state: {
        question: `Tell me about ${title}`,
        level,
        fromHome: true,
      },
    });
  };

  // =====================================================
  // UI
  // =====================================================

  return (
    <div className={`home-page ${darkMode ? "dark" : "light"}`}>

      {/* =================================================
          NAVBAR
      ================================================= */}

      <nav className="home-navbar">

        {/* BRAND */}
        <div className="home-logo">

          <div className="home-logo-icon">
            <FaBookMedical />
          </div>

          <div>
            <h2>FMT@Fingertips</h2>
            <span>Forensic Medicine Assistant</span>
          </div>

        </div>

        {/* NAVIGATION */}
        <div className="home-nav-links">

          {/* DARK MODE */}
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            title={
              darkMode
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
            aria-label="Toggle dark mode"
          >
            {darkMode ? <FaSun /> : <FaMoon />}
          </button>

          {/* HISTORY */}
          <button
            type="button"
            onClick={() => navigate("/history")}
          >
            <FaHistory />
            <span>History</span>
          </button>

          {/* PROFILE */}
          <button
            type="button"
            onClick={() => navigate("/profile")}
          >
            <FaUserCircle />
            <span>Profile</span>
          </button>

        </div>

      </nav>

      {/* =================================================
          MAIN CONTENT
      ================================================= */}

      <main className="home-content">

        {/* =================================================
            HERO
        ================================================= */}

        <div className="home-hero">

          {/* BADGE */}
          <div className="hero-badge">
            ✦ AI-Powered FMT Learning
          </div>

          {/* MAIN TITLE */}
          <h1>
            Your Forensic Medicine
            <br />
            <span>
              Assistant at Your Fingertips
            </span>
          </h1>

          {/* CREATOR CREDIT */}
          <div className="creator-credit">

            <span className="credit-line"></span>

            <span>
              Created by{" "}
              <strong>Dr. Kanchan Zine</strong>
            </span>

            <span className="credit-line"></span>

          </div>

          {/* HERO DESCRIPTION */}
          <p>
            Ask questions, revise concepts, and explore your FMT
            study material with an intelligent learning assistant.
          </p>

        </div>

        {/* =================================================
            LEARNING LEVEL
        ================================================= */}

        <section className="learning-level-section">

          <div className="learning-level-heading">

            <div>

              <h3>
                Choose your learning level
              </h3>

              <p>
                Select the level that matches your current studies.
              </p>

            </div>

            <div className="selected-level-label">

              <span></span>

              {level} mode selected

            </div>

          </div>

          {/* LEVEL CARDS */}

          <div className="level-cards">

            {/* =================================================
                UG
            ================================================= */}

            <button
              type="button"
              className={`level-card ${
                level === "UG" ? "selected" : ""
              }`}
              onClick={() => setLevel("UG")}
            >

              <div className="level-card-top">

                <div className="level-icon ug-icon">
                  <FaBookMedical />
                </div>

                {level === "UG" && (
                  <div className="level-check">
                    <FaCheck />
                  </div>
                )}

              </div>

              <div className="level-small-title">
                UNDERGRADUATE
              </div>

              <h2>
                UG
              </h2>

              <p>
                Clear, exam-oriented explanations designed for
                undergraduate medical students.
              </p>

              <div className="level-tags">

                <span>
                  MBBS
                </span>

                <span>
                  Exam Focused
                </span>

                <span>
                  Rapid Revision
                </span>

              </div>

              <div className="level-arrow">
                <FaArrowRight />
              </div>

            </button>

            {/* =================================================
                PG
            ================================================= */}

            <button
              type="button"
              className={`level-card ${
                level === "PG" ? "selected" : ""
              }`}
              onClick={() => setLevel("PG")}
            >

              <div className="level-card-top">

                <div className="level-icon pg-icon">
                  <FaGraduationCap />
                </div>

                {level === "PG" && (
                  <div className="level-check">
                    <FaCheck />
                  </div>
                )}

              </div>

              <div className="level-small-title">
                POSTGRADUATE
              </div>

              <h2>
                PG
              </h2>

              <p>
                Advanced and detailed explanations for
                postgraduate medical learning.
              </p>

              <div className="level-tags">

                <span>
                  MD / MS
                </span>

                <span>
                  Advanced
                </span>

                <span>
                  In-depth
                </span>

              </div>

              <div className="level-arrow">
                <FaArrowRight />
              </div>

            </button>

          </div>

        </section>

        {/* =================================================
            SEARCH
        ================================================= */}

        <form
          className="home-search"
          onSubmit={handleSearch}
        >

          <FaSearch className="search-icon" />

          <input
            name="question"
            type="text"
            placeholder={`Ask your ${level} FMT question...`}
          />

          <button type="submit">
            <FaArrowRight />
          </button>

        </form>

        {/* =================================================
            ANSWER MODE
        ================================================= */}

        <div className="answer-mode">

          <FaGraduationCap />

          <span>
            Answer mode:
          </span>

          <strong>
            {level}
          </strong>

        </div>

        {/* =================================================
            TOPICS
        ================================================= */}

        <section className="suggestions-section">

          <div className="section-heading">

            <h3>
              Explore FMT Topics
            </h3>

            <span>
              Start with a topic
            </span>

          </div>

          <div className="suggestion-grid">

            {suggestions.map((item) => (

              <button
                type="button"
                className="suggestion-card"
                key={item.title}
                onClick={() => openTopic(item.title)}
              >

                <div className="suggestion-icon">
                  {item.icon}
                </div>

                <div className="suggestion-text">

                  <h4>
                    {item.title}
                  </h4>

                  <p>
                    {item.text}
                  </p>

                </div>

                <FaArrowRight
                  className="suggestion-arrow"
                />

              </button>

            ))}

          </div>

        </section>

        {/* =================================================
            FOOTER
        ================================================= */}

        <div className="home-footer">

          <span>
            📚 Built for Medical Students
          </span>

          <span>
            •
          </span>

          <span>
            Study smarter with FMT@Fingertips
          </span>

        </div>

      </main>

    </div>
  );
}

export default Home;