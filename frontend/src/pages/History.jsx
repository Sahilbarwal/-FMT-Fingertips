import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaBookMedical,
  FaArrowLeft,
  FaSearch,
  FaTrash,
  FaCommentMedical,
  FaUserCircle,
} from "react-icons/fa";
import axios from "axios";

function History() {
  const navigate = useNavigate();

  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  // =====================================================
  // LOAD HISTORY FROM DJANGO
  // =====================================================

  useEffect(() => {
    const token = localStorage.getItem("access");

    if (!token) {
      navigate("/login");
      return;
    }

    axios
      .get("https://fmt-fingertips-backend.onrender.com/history/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        console.log("History data:", response.data);
        setHistory(response.data);
      })
      .catch((error) => {
        console.log("History error:", error);

        if (error.response?.status === 401) {
          localStorage.removeItem("access");
          navigate("/login");
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, [navigate]);

  // =====================================================
  // DELETE ALL HISTORY
  // =====================================================

  const handleClearHistory = async () => {
    const token = localStorage.getItem("access");

    if (!token) {
      navigate("/login");
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to clear your entire search history?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await axios.delete("https://fmt-fingertips-backend.onrender.com/history/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setHistory([]);

      alert("History cleared successfully.");
    } catch (error) {
      console.log("Clear history error:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access");
        navigate("/login");
      } else {
        alert("Unable to clear history.");
      }
    }
  };

  // =====================================================
  // OPEN QUESTION
  // =====================================================

  const handleOpenChat = (question) => {
    navigate("/chat", {
      state: {
        question,
      },
    });
  };

  // =====================================================
  // FORMAT DATE
  // =====================================================

  const formatDate = (dateString) => {
    if (!dateString) {
      return "";
    }

    const date = new Date(dateString);

    const today = new Date();

    const yesterday = new Date();
    yesterday.setDate(today.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Today";
    }

    if (date.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    }

    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
    });
  };

  // =====================================================
  // FORMAT TIME
  // =====================================================

  const formatTime = (dateString) => {
    if (!dateString) {
      return "";
    }

    const date = new Date(dateString);

    return date.toLocaleTimeString("en-IN", {
      hour: "numeric",
      minute: "2-digit",
    });
  };

  // =====================================================
  // SEARCH HISTORY
  // =====================================================

  const filteredHistory = history.filter((item) =>
    item.question.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="history-page">

      {/* Navbar */}
      <nav className="history-navbar">

        <div className="history-brand">

          <div className="history-brand-icon">
            <FaBookMedical />
          </div>

          <div>
            <h2>FMT@Fingertips</h2>
            <span>Forensic Medicine Assistant</span>
          </div>

        </div>

        <button
          className="history-profile-button"
          onClick={() => navigate("/profile")}
        >
          <FaUserCircle />
          Profile
        </button>

      </nav>

      {/* Main */}
      <main className="history-container">

        <button
          className="history-back"
          onClick={() => navigate("/")}
        >
          <FaArrowLeft />
          Back to Home
        </button>

        {/* Heading */}
        <div className="history-heading">

          <div>
            <h1>Search History</h1>

            <p>
              Revisit your previous FMT questions and conversations.
            </p>
          </div>

          <button
            className="new-chat-button"
            onClick={() => navigate("/chat")}
          >
            <FaCommentMedical />
            New Chat
          </button>

        </div>

        {/* History Card */}
        <div className="history-card">

          {/* Search */}
          <div className="history-search">

            <FaSearch />

            <input
              type="text"
              placeholder="Search your previous questions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />

          </div>

          {/* Loading */}
          {loading && (
            <div className="history-empty">
              <p>Loading your history...</p>
            </div>
          )}

          {/* History List */}
          {!loading && filteredHistory.length > 0 && (

            <div className="history-list">

              {filteredHistory.map((item) => (

                <div
                  className="history-item"
                  key={item.id}
                >

                  <button
                    className="history-question"
                    onClick={() => handleOpenChat(item.question)}
                  >

                    <div className="history-question-icon">
                      <FaCommentMedical />
                    </div>

                    <div className="history-question-text">

                      <h3>
                        {item.question}
                      </h3>

                      <span>
                        {formatDate(item.created_at)} •{" "}
                        {formatTime(item.created_at)}
                      </span>

                    </div>

                  </button>

                </div>

              ))}

            </div>

          )}

          {/* No history */}
          {!loading && filteredHistory.length === 0 && (

            <div className="history-empty">

              <FaCommentMedical />

              <h3>
                {search
                  ? "No matching questions"
                  : "No search history yet"}
              </h3>

              <p>
                {search
                  ? "Try a different search term."
                  : "Your FMT questions will appear here."}
              </p>

            </div>

          )}

        </div>

        {/* Clear History */}
        {!loading && history.length > 0 && (

          <button
            className="clear-history-button"
            onClick={handleClearHistory}
          >
            <FaTrash />
            Clear History
          </button>

        )}

        <p className="history-note">
          Your personal search history will be securely stored with your account.
        </p>

      </main>

    </div>
  );
}

export default History;