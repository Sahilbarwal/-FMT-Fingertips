import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useLocation } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import axios from "axios";

import {
  Bot,
  Plus,
  History,
  User,
  Mail,
  Calendar,
  Settings,
  MessageSquare,
  MoreVertical,
  GraduationCap,
  Paperclip,
  Send,
  Moon,
  Sun,
  ChevronDown,
  LoaderCircle,
  FileText,
  LogOut,
  Trash2,
  Search,
  X,
} from "lucide-react";

import "../styles/chat.css";
import "../styles/history.css";
import "../styles/profile.css";

const API_URL = "http://127.0.0.1:8000/ask/";
const CHAT_STORAGE_KEY = "fmt_recent_chats";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [level, setLevel] = useState("PG");
  const [darkMode, setDarkMode] = useState(false);

  const [messages, setMessages] = useState([]);
  const [recentChats, setRecentChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);

  const [openChatMenu, setOpenChatMenu] = useState(null);
  const [studentMenuOpen, setStudentMenuOpen] = useState(false);

  // "chat"  -> normal chat header + messages + input
  // "history" -> full history browser in the main area
  const [view, setView] = useState("chat");
  const [historySearch, setHistorySearch] = useState("");
  const [historyItems, setHistoryItems] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  const chatEndRef = useRef(null);
  const textareaRef = useRef(null);

  // =========================================================
  // LOAD SAVED CHATS
  // =========================================================

  useEffect(() => {
    try {
      const savedChats = localStorage.getItem(CHAT_STORAGE_KEY);

      if (savedChats) {
        const parsedChats = JSON.parse(savedChats);

        if (Array.isArray(parsedChats)) {
          setRecentChats(parsedChats);
        }
      }
    } catch (error) {
      console.error("Could not load recent chats:", error);
    }
  }, []);

  // =========================================================
  // SCROLL TO LATEST MESSAGE
  // =========================================================

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  // =========================================================
  // AUTO RESIZE TEXTAREA
  // =========================================================

  useEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "auto";

    textarea.style.height =
      `${Math.min(textarea.scrollHeight, 150)}px`;
  }, [question]);

  // =========================================================
  // FORMAT TIME
  // =========================================================

  const formatTime = (time) => {
    if (!time) return "";

    return new Date(time).toLocaleTimeString(
      [],
      {
        hour: "numeric",
        minute: "2-digit",
      }
    );
  };

  // =========================================================
  // FETCH SERVER HISTORY WHEN THE HISTORY VIEW OPENS
  // =========================================================

  useEffect(() => {
    if (view !== "history") return;

    const token = localStorage.getItem("access");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    setHistoryLoading(true);

    axios
      .get("http://127.0.0.1:8000/history/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        setHistoryItems(response.data);
      })
      .catch((error) => {
        console.error("History error:", error);

        if (error.response?.status === 401) {
          localStorage.removeItem("access");
          window.location.href = "/login";
        }
      })
      .finally(() => {
        setHistoryLoading(false);
      });
  }, [view]);

  // =========================================================
  // FETCH PROFILE WHEN THE PROFILE VIEW OPENS
  // =========================================================

  useEffect(() => {
    if (view !== "profile") return;

    const token = localStorage.getItem("access");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    setProfileLoading(true);

    axios
      .get("http://127.0.0.1:8000/me/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        setProfileData(response.data);
      })
      .catch((error) => {
        console.error("Profile error:", error);

        if (error.response?.status === 401) {
          localStorage.removeItem("access");
          window.location.href = "/login";
        }
      })
      .finally(() => {
        setProfileLoading(false);
      });
  }, [view]);

  // =========================================================
  // FORMAT HISTORY DATE ("Today" / "Yesterday" / "27 Aug")
  // =========================================================

  const formatHistoryDate = (dateString) => {
    if (!dateString) return "";

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

  // =========================================================
  // FILTERED HISTORY (client-side search)
  // =========================================================

  const filteredHistory = historyItems.filter((item) =>
    item.question
      .toLowerCase()
      .includes(historySearch.toLowerCase())
  );

  // =========================================================
  // OPEN A HISTORY QUESTION BACK INTO THE CHAT
  // =========================================================

  const handleOpenHistoryItem = (question) => {
    setView("chat");
    setQuestion(question);

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  // =========================================================
  // CLEAR ALL SERVER HISTORY
  // =========================================================

  const handleClearHistory = async () => {
    const token = localStorage.getItem("access");

    if (!token) {
      window.location.href = "/login";
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to clear your entire search history?"
    );

    if (!confirmed) return;

    try {
      await axios.delete("http://127.0.0.1:8000/history/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setHistoryItems([]);
    } catch (error) {
      console.error("Clear history error:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access");
        window.location.href = "/login";
      } else {
        alert("Unable to clear history.");
      }
    }
  };

  // =========================================================
  // PERSIST CHATS TO LOCALSTORAGE
  // (pure side-effect helper only — never derives the next
  //  state, so it can never read stale data)
  // =========================================================

  const persistChats = (chats) => {
    try {
      localStorage.setItem(
        CHAT_STORAGE_KEY,
        JSON.stringify(chats)
      );
    } catch (error) {
      console.error("Could not save chats:", error);
    }
  };

  // =========================================================
  // CREATE CHAT
  // =========================================================
  //
  // FIX: uses the functional form of setRecentChats so the
  // "prepend new chat" step always operates on the freshest
  // state, instead of the `recentChats` value captured when
  // sendQuestion started running.
  // =========================================================

  const createChat = (
    firstQuestion,
    chatMessages,
    chatLevel = level
  ) => {
    const newChat = {
      id: Date.now(),
      title: firstQuestion,
      time: "Just now",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      level: chatLevel,
      messages: chatMessages,
    };

    setRecentChats((prevChats) => {
      const updatedChats = [
        newChat,
        ...prevChats,
      ].slice(0, 20);

      persistChats(updatedChats);

      return updatedChats;
    });

    return newChat;
  };

  // =========================================================
  // UPDATE EXISTING CHAT
  // =========================================================
  //
  // FIX: same functional-update fix as createChat. This is
  // the call that was previously wiping out a just-created
  // chat once the assistant's response arrived, because it
  // was mapping over a stale `recentChats` snapshot that
  // didn't include the chat createChat had just added.
  // =========================================================

  const updateChat = (
    chatId,
    updatedMessages
  ) => {
    setRecentChats((prevChats) => {
      const updatedChats = prevChats.map(
        (chat) => {
          if (chat.id === chatId) {
            return {
              ...chat,
              messages: updatedMessages,
              updatedAt:
                new Date().toISOString(),
              time: "Just now",
            };
          }

          return chat;
        }
      );

      persistChats(updatedChats);

      return updatedChats;
    });
  };

  // =========================================================
  // SEND QUESTION
  // =========================================================

  const sendQuestion = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedQuestion,
      time: new Date().toISOString(),
    };

    const messagesWithUser = [
      ...messages,
      userMessage,
    ];

    setMessages(messagesWithUser);

    setQuestion("");
    setLoading(true);

    // -------------------------------------------------------
    // CREATE NEW CHAT IF NO ACTIVE CHAT
    // -------------------------------------------------------

    let currentChatId = activeChatId;

    if (!currentChatId) {
      const newChat = createChat(
        trimmedQuestion,
        messagesWithUser,
        level
      );

      currentChatId = newChat.id;

      setActiveChatId(newChat.id);
    } else {
      updateChat(
        currentChatId,
        messagesWithUser
      );
    }

    try {
      // Your token is stored as "access"
      const token =
        localStorage.getItem("access");

      if (!token) {
        throw new Error(
          "No login token found. Please log in again."
        );
      }

      const response = await fetch(
        API_URL,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${token}`,
          },

          body: JSON.stringify({
            question: trimmedQuestion,
            level: level,
          }),
        }
      );

      // -----------------------------------------------------
      // HANDLE UNAUTHORIZED
      // -----------------------------------------------------

      if (response.status === 401) {
        throw new Error(
          "Your session is unauthorized or expired. Please log in again."
        );
      }

      // -----------------------------------------------------
      // HANDLE OTHER ERRORS
      // -----------------------------------------------------

      if (!response.ok) {
        let errorMessage =
          "Unable to get answer from server.";

        try {
          const errorData =
            await response.json();

          errorMessage =
            errorData.detail ||
            errorData.error ||
            errorData.message ||
            errorMessage;
        } catch {
          // Keep default error message
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",

        content:
          data.answer ||
          data.response ||
          data.message ||
          "No answer was returned.",

        sources:
          data.sources || [],

        time:
          new Date().toISOString(),
      };

      const finalMessages = [
        ...messagesWithUser,
        assistantMessage,
      ];

      setMessages(finalMessages);

      updateChat(
        currentChatId,
        finalMessages
      );
    } catch (error) {
      console.error(
        "ASK ERROR:",
        error
      );

      const errorMessage = {
        id: Date.now() + 2,
        role: "assistant",
        error: true,

        content:
          error.message ||
          "Something went wrong while generating the answer.",

        time:
          new Date().toISOString(),
      };

      const finalMessages = [
        ...messagesWithUser,
        errorMessage,
      ];

      setMessages(finalMessages);

      updateChat(
        currentChatId,
        finalMessages
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ENTER TO SEND
  // =========================================================

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendQuestion();
    }
  };

  // =========================================================
  // NEW CHAT
  // =========================================================

  const handleNewChat = () => {
    setMessages([]);
    setQuestion("");
    setActiveChatId(null);
    setOpenChatMenu(null);
    setView("chat");

    setTimeout(() => {
      textareaRef.current?.focus();
    }, 100);
  };

  // =========================================================
  // OPEN CHAT
  // =========================================================

  const openChat = (chat) => {
    if (loading) return;

    setMessages(chat.messages || []);
    setActiveChatId(chat.id);

    if (chat.level) {
      setLevel(chat.level);
    }

    setOpenChatMenu(null);
    setView("chat");

    setTimeout(() => {
      chatEndRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }, 100);
  };

  // =========================================================
  // DELETE CHAT
  // =========================================================

  const deleteChat = (
    event,
    chatId
  ) => {
    event.stopPropagation();

    setRecentChats((prevChats) => {
      const updatedChats = prevChats.filter(
        (chat) => chat.id !== chatId
      );

      persistChats(updatedChats);

      return updatedChats;
    });

    setOpenChatMenu(null);

    if (activeChatId === chatId) {
      setMessages([]);
      setActiveChatId(null);
      setQuestion("");
    }
  };

  // =========================================================
  // CLEAR ALL CHATS
  // =========================================================

  const clearAllChats = () => {
    setRecentChats(() => {
      persistChats([]);
      return [];
    });

    setMessages([]);
    setActiveChatId(null);
    setQuestion("");
    setOpenChatMenu(null);
  };

  // =========================================================
  // SWITCH LEVEL
  // =========================================================

  const switchLevel = () => {
    setLevel((currentLevel) =>
      currentLevel === "UG"
        ? "PG"
        : "UG"
    );
  };

  // =========================================================
  // TOGGLE STUDENT MENU
  // =========================================================

  const toggleStudentMenu = () => {
    setStudentMenuOpen(
      !studentMenuOpen
    );
  };

  // =========================================================
  // PROFILE
  // =========================================================

  const handleProfile = () => {
    setStudentMenuOpen(false);
    setView("profile");
  };

  // =========================================================
  // LOGOUT
  // =========================================================

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    window.location.href = "/login";
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div
      className={
        darkMode
          ? "chat-app dark"
          : "chat-app"
      }
    >

      {/* ================================================= */}
      {/* SIDEBAR */}
      {/* ================================================= */}

      <aside className="chat-sidebar">

        {/* BRAND */}

        <div className="sidebar-brand">

          <div className="brand-icon">
            <FileText size={21} />
          </div>

          <div>

            <h1>
              FMT@Fingertips
            </h1>

            <span>
              Forensic Medicine Assistant
            </span>

          </div>

        </div>


        {/* NEW CHAT */}

        <button
          className="new-chat-btn"
          onClick={handleNewChat}
        >

          <Plus size={19} />

          <span>
            New Chat
          </span>

        </button>


        {/* NAVIGATION */}

        <nav className="sidebar-nav">

          <button
            className={
              view === "history"
                ? "active"
                : ""
            }
            onClick={() =>
              setView("history")
            }
          >
            <History size={19} />

            <span>
              History
            </span>
          </button>


          <button
            className={
              view === "profile"
                ? "active"
                : ""
            }
            onClick={() =>
              setView("profile")
            }
          >
            <User size={19} />

            <span>
              Profile
            </span>
          </button>


          <button>
            <Settings size={19} />

            <span>
              Settings
            </span>
          </button>

        </nav>


        {/* RECENT CHATS */}

        <div className="recent-section">

          <div className="recent-header">

            <span>
              Recent Chats
            </span>


            {recentChats.length > 0 && (

              <button
                onClick={clearAllChats}
              >
                Clear all
              </button>

            )}

          </div>


          <div className="recent-list">

            {recentChats.length === 0 ? (

              <div className="empty-history">

                <MessageSquare
                  size={22}
                />

                <p>
                  Your recent chats will appear here.
                </p>

              </div>

            ) : (

              recentChats.map(
                (chat) => (

                  <div
                    key={chat.id}
                    className={
                      activeChatId === chat.id
                        ? "recent-chat active"
                        : "recent-chat"
                    }
                  >

                    {/* CHAT OPEN BUTTON */}

                    <button
                      className="recent-chat-main"
                      onClick={() =>
                        openChat(chat)
                      }
                    >

                      <MessageSquare
                        size={18}
                      />

                      <div className="recent-chat-text">

                        <strong>
                          {chat.title}
                        </strong>

                        <span>
                          {chat.time ||
                            "Recent"}
                        </span>

                      </div>

                    </button>


                    {/* THREE DOT BUTTON */}

                    <button
                      className="chat-options-btn"
                      onClick={(event) => {
                        event.stopPropagation();

                        setOpenChatMenu(
                          openChatMenu ===
                            chat.id
                            ? null
                            : chat.id
                        );
                      }}
                    >

                      <MoreVertical
                        size={18}
                      />

                    </button>


                    {/* DELETE MENU */}

                    {openChatMenu ===
                      chat.id && (

                      <div
                        className="chat-options-menu"
                      >

                        <button
                          onClick={(event) =>
                            deleteChat(
                              event,
                              chat.id
                            )
                          }
                        >

                          <Trash2
                            size={16}
                          />

                          <span>
                            Delete
                          </span>

                        </button>

                      </div>

                    )}

                  </div>

                )
              )

            )}

          </div>

        </div>


        {/* MODE CARD */}

        <div className="mode-card">

          <div className="mode-card-icon">

            <GraduationCap
              size={25}
            />

          </div>


          <div className="mode-card-content">

            <h3>
              {level} Mode
            </h3>

            <p>
              {level === "UG"
                ? "Simple and exam-focused explanations for undergraduate students."
                : "Advanced and detailed explanations for postgraduate learning."}
            </p>

          </div>


          <button
            className="switch-mode-btn"
            onClick={switchLevel}
          >

            Switch to{" "}

            {level === "UG"
              ? "PG"
              : "UG"}

            <span>
              →
            </span>

          </button>

        </div>

      </aside>


      {/* ================================================= */}
      {/* MAIN AREA */}
      {/* ================================================= */}

      <main className="chat-main">


        {/* ================================================= */}
        {/* TOP BAR */}
        {/* ================================================= */}

        <header className="chat-topbar">


          <div className="mobile-brand">

            <div className="mobile-brand-icon">
              <Bot size={20} />
            </div>


            <div>

              <strong>
                FMT Assistant
              </strong>

              <span>
                {level} Learning
              </span>

            </div>

          </div>


          <div className="topbar-right">


            {/* DARK MODE */}

            <button
              className="theme-toggle"
              onClick={() =>
                setDarkMode(
                  !darkMode
                )
              }
              title={
                darkMode
                  ? "Switch to light mode"
                  : "Switch to dark mode"
              }
            >

              <div
                className={
                  darkMode
                    ? "theme-switch active"
                    : "theme-switch"
                }
              >

                <div className="theme-switch-knob">

                  {darkMode ? (
                    <Sun size={15} />
                  ) : (
                    <Moon size={15} />
                  )}

                </div>

              </div>

              <span>
                {darkMode
                  ? "Light"
                  : "Dark"}
              </span>

            </button>


            {/* STUDENT MENU */}

            <div className="student-menu-wrapper">

              <button
                className="student-menu"
                onClick={toggleStudentMenu}
              >

                <div className="student-avatar">
                  S
                </div>

                <span>
                  Student
                </span>

                <ChevronDown
                  size={16}
                  className={
                    studentMenuOpen
                      ? "chevron-open"
                      : ""
                  }
                />

              </button>


              {studentMenuOpen && (

                <div className="student-dropdown">

                  <button
                    onClick={handleProfile}
                  >

                    <User size={17} />

                    <span>
                      Profile
                    </span>

                  </button>


                  <button
                    className="logout-option"
                    onClick={handleLogout}
                  >

                    <LogOut size={17} />

                    <span>
                      Logout
                    </span>

                  </button>

                </div>

              )}

            </div>

          </div>

        </header>


        {view === "chat" && (
        <>

        {/* ================================================= */}
        {/* CHAT HEADER */}
        {/* ================================================= */}

        <div className="chat-header">

          <div className="assistant-avatar">
            <Bot size={27} />
          </div>


          <div>

            <div className="assistant-title-row">

              <h2>
                FMT Assistant
              </h2>


              <span className="level-badge">

                <GraduationCap
                  size={13}
                />

                {level}

              </span>

            </div>


            <p>
              {level === "UG"
                ? "Undergraduate • Exam-oriented FMT learning"
                : "Postgraduate • Advanced FMT learning"}
            </p>

          </div>

        </div>


        {/* ================================================= */}
        {/* CHAT CONTENT */}
        {/* ================================================= */}

        <div className="chat-scroll-area">

          <div className="chat-content">


            {/* EMPTY STATE */}

            {messages.length === 0 &&
              !loading && (

                <div className="welcome-state">

                  <div className="welcome-icon">
                    <Bot size={34} />
                  </div>


                  <h2>
                    Ask your FMT question
                  </h2>


                  <p>
                    Get detailed,
                    textbook-grounded answers
                    for your forensic medicine
                    studies.
                  </p>


                  <div className="suggestion-grid">


                    <button
                      onClick={() =>
                        setQuestion(
                          "What is rigor mortis?"
                        )
                      }
                    >
                      What is rigor mortis?
                    </button>


                    <button
                      onClick={() =>
                        setQuestion(
                          "Explain mechanical asphyxia."
                        )
                      }
                    >
                      Mechanical asphyxia
                    </button>


                    <button
                      onClick={() =>
                        setQuestion(
                          "Explain postmortem changes."
                        )
                      }
                    >
                      Postmortem changes
                    </button>


                    <button
                      onClick={() =>
                        setQuestion(
                          "Define abrasion."
                        )
                      }
                    >
                      Define abrasion
                    </button>

                  </div>

                </div>

              )}


            {/* MESSAGES */}

            {messages.map(
              (message) => (

                <div
                  key={message.id}
                  className={
                    message.role === "user"
                      ? "message-row user-row"
                      : "message-row assistant-row"
                  }
                >


                  {/* ASSISTANT */}

                  {message.role ===
                    "assistant" && (

                    <>

                      <div className="message-assistant-icon">
                        <Bot size={22} />
                      </div>


                      <div className="assistant-message-wrap">


                        <div className="message-meta">

                          <span>
                            FMT Assistant
                          </span>

                          <span>
                            •
                          </span>

                          <span>
                            {formatTime(
                              message.time
                            )}
                          </span>

                        </div>


                        <div
                          className={
                            message.error
                              ? "assistant-answer error-answer"
                              : "assistant-answer"
                          }
                        >

                          <ReactMarkdown
                            remarkPlugins={[
                              remarkGfm,
                            ]}
                          >
                            {message.content}
                          </ReactMarkdown>

                        </div>


                        {/* SOURCES */}

                        {message.sources &&
                          message.sources.length >
                            0 && (

                            <div className="answer-sources">


                              <div className="sources-title">

                                <FileText
                                  size={17}
                                />

                                <span>
                                  FMT Material Used
                                </span>

                              </div>


                              <div className="sources-list">

                                {message.sources.map(
                                  (
                                    source,
                                    index
                                  ) => (

                                    <div
                                      key={index}
                                      className="source-item"
                                    >

                                      <strong>
                                        {source.source}
                                      </strong>

                                      <span>
                                        • Chunk{" "}
                                        {source.chunk}
                                      </span>

                                    </div>

                                  )
                                )}

                              </div>

                            </div>

                          )}

                      </div>

                    </>

                  )}


                  {/* USER */}

                  {message.role ===
                    "user" && (

                    <div className="user-message-wrap">


                      <div className="message-meta user-meta">

                        <span>
                          You
                        </span>

                        <span>
                          •
                        </span>

                        <span>
                          {formatTime(
                            message.time
                          )}
                        </span>

                      </div>


                      <div className="user-message-content">

                        {message.content}

                      </div>

                    </div>

                  )}

                </div>

              )
            )}


            {/* LOADING */}

            {loading && (

              <div className="message-row assistant-row">


                <div className="message-assistant-icon">

                  <Bot size={22} />

                </div>


                <div className="loading-answer">

                  <LoaderCircle
                    size={22}
                    className="spinner"
                  />


                  <div>

                    <strong>
                      Searching FMT material
                    </strong>

                    <span>
                      Generating your answer...
                    </span>

                  </div>

                </div>

              </div>

            )}


            <div
              ref={chatEndRef}
            />

          </div>

        </div>


        {/* ================================================= */}
        {/* INPUT */}
        {/* ================================================= */}

        <div className="chat-input-area">

          <div className="chat-input-box">


            <button
              className="attach-btn"
              type="button"
            >
              <Paperclip size={21} />
            </button>


            <textarea
              ref={textareaRef}

              value={question}

              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }

              onKeyDown={handleKeyDown}

              placeholder={`Ask your ${level} FMT question...`}

              rows="1"

              disabled={loading}
            />


            <button
              className="send-btn"

              onClick={sendQuestion}

              disabled={
                loading ||
                !question.trim()
              }
            >

              {loading ? (

                <LoaderCircle
                  size={20}
                  className="spinner"
                />

              ) : (

                <Send size={20} />

              )}

            </button>

          </div>


          <p className="chat-disclaimer">

            FMT@Fingertips is an educational assistant.
            Always verify important medical and legal
            information with authoritative sources.

          </p>

        </div>

        </>
        )}


        {/* ================================================= */}
        {/* HISTORY VIEW (embedded — sidebar stays untouched) */}
        {/* ================================================= */}

        {view === "history" && (

          <div className="history-embedded">

            <div className="history-heading">

              <div>
                <h1>Search History</h1>

                <p>
                  Revisit your previous FMT questions and conversations.
                </p>
              </div>

              <button
                className="new-chat-button"
                onClick={handleNewChat}
              >
                <Plus size={16} />
                New Chat
              </button>

            </div>

            <div className="history-card">

              {/* Search */}

              <div className="history-search">

                <Search size={16} />

                <input
                  type="text"
                  placeholder="Search your previous questions..."
                  value={historySearch}
                  onChange={(event) =>
                    setHistorySearch(event.target.value)
                  }
                />

              </div>

              {/* Loading */}

              {historyLoading && (
                <div className="history-empty">
                  <p>Loading your history...</p>
                </div>
              )}

              {/* History List */}

              {!historyLoading &&
                filteredHistory.length > 0 && (

                  <div className="history-list">

                    {filteredHistory.map((item) => (

                      <div
                        className="history-item"
                        key={item.id}
                      >

                        <button
                          className="history-question"
                          onClick={() =>
                            handleOpenHistoryItem(
                              item.question
                            )
                          }
                        >

                          <div className="history-question-icon">
                            <MessageSquare size={16} />
                          </div>

                          <div className="history-question-text">

                            <h3>
                              {item.question}
                            </h3>

                            <span>
                              {formatHistoryDate(
                                item.created_at
                              )}{" "}
                              •{" "}
                              {formatTime(
                                item.created_at
                              )}
                            </span>

                          </div>

                        </button>

                      </div>

                    ))}

                  </div>

                )}

              {/* No history */}

              {!historyLoading &&
                filteredHistory.length === 0 && (

                  <div className="history-empty">

                    <MessageSquare size={28} />

                    <h3>
                      {historySearch
                        ? "No matching questions"
                        : "No search history yet"}
                    </h3>

                    <p>
                      {historySearch
                        ? "Try a different search term."
                        : "Your FMT questions will appear here."}
                    </p>

                  </div>

                )}

            </div>

            {/* Clear History */}

            {!historyLoading &&
              historyItems.length > 0 && (

                <button
                  className="clear-history-button"
                  onClick={handleClearHistory}
                >
                  <Trash2 size={16} />
                  Clear History
                </button>

              )}

            <p className="history-note">
              Your personal search history will be securely stored
              with your account.
            </p>

          </div>

        )}


        {/* ================================================= */}
        {/* PROFILE VIEW (embedded — sidebar stays untouched) */}
        {/* ================================================= */}

        {view === "profile" && (

          <div className="profile-embedded">

            <div className="profile-heading">

              <div>
                <h1>Your Profile</h1>

                <p>
                  Manage your account details and preferences.
                </p>
              </div>

            </div>

            {/* Loading */}

            {profileLoading && (
              <div className="history-empty">
                <p>Loading your profile...</p>
              </div>
            )}

            {/* Loaded */}

            {!profileLoading && profileData && (

              <div className="profile-card">

                <div className="profile-header">

                  <div className="profile-avatar">
                    <User size={38} />
                  </div>

                  <div>
                    <h1>{profileData.username}</h1>
                    <p>{profileData.email}</p>
                  </div>

                </div>

                <div className="profile-section">

                  <h2>Account Information</h2>

                  <div className="profile-info">

                    <div className="profile-info-item">

                      <div className="profile-info-icon">
                        <User size={18} />
                      </div>

                      <div>
                        <span>Username</span>
                        <strong>{profileData.username}</strong>
                      </div>

                    </div>

                    <div className="profile-info-item">

                      <div className="profile-info-icon">
                        <Mail size={18} />
                      </div>

                      <div>
                        <span>Email</span>
                        <strong>{profileData.email}</strong>
                      </div>

                    </div>

                    <div className="profile-info-item">

                      <div className="profile-info-icon">
                        <Calendar size={18} />
                      </div>

                      <div>
                        <span>Account ID</span>
                        <strong>{profileData.id}</strong>
                      </div>

                    </div>

                  </div>

                </div>

                <div className="profile-section">

                  <h2>Quick Actions</h2>

                  <button
                    className="profile-action"
                    onClick={() => setView("history")}
                  >
                    <div>
                      <History size={16} />
                    </div>

                    <span>View Search History</span>
                  </button>

                </div>

                <button
                  className="logout-button"
                  onClick={handleLogout}
                >
                  <LogOut size={16} />
                  Logout
                </button>

              </div>

            )}

            {/* Failed to load */}

            {!profileLoading &&
              !profileData && (

                <div className="history-empty">

                  <User size={28} />

                  <h3>
                    Unable to load profile
                  </h3>

                  <p>
                    Please try again in a moment.
                  </p>

                </div>

              )}

            <p className="profile-footer">
              FMT@Fingertips • Your Forensic Medicine Learning
              Assistant
            </p>

          </div>

        )}

      </main>

    </div>
  );
}