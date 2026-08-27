import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
    FaRobot,
    FaUser,
    FaCopy,
    FaCheck,
    FaTrash,
    FaPaperPlane,
    FaBook,
} from "react-icons/fa";

function ChatBox() {

    const [question, setQuestion] = useState("");
    const [level, setLevel] = useState("UG");

    const [messages, setMessages] = useState([]);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [copiedIndex, setCopiedIndex] = useState(null);


    /* =========================================
       SUGGESTED QUESTIONS
    ========================================= */

    const suggestedQuestions = [
        "What is rigor mortis?",
        "Define livor mortis.",
        "What is an abrasion?",
        "Explain the mechanism of rigor mortis.",
        "Differentiate rigor mortis and cadaveric spasm.",
    ];


    /* =========================================
       ASK QUESTION
    ========================================= */

    const askQuestion = async (customQuestion = null) => {

        const finalQuestion =
            customQuestion || question.trim();

        if (!finalQuestion.trim() || loading) {
            return;
        }

        setError("");

        const userMessage = {
            type: "user",
            content: finalQuestion,
        };


        /* Add user question to history */

        setMessages((previousMessages) => [
            ...previousMessages,
            userMessage,
        ]);


        setQuestion("");

        setLoading(true);


        try {

            const token =
                localStorage.getItem("access");


            if (!token) {

                setError("Please login first.");

                setLoading(false);

                return;
            }


            const response =
                await fetch(
                    "http://127.0.0.1:8000/ask/",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json",

                            Authorization:
                                `Bearer ${token}`,
                        },

                        body: JSON.stringify({
                            question:
                                finalQuestion,

                            level:
                                level,
                        }),
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    data.error ||
                    "Something went wrong."
                );

            }


            /* Add AI answer to history */

            const assistantMessage = {
                type: "assistant",

                content:
                    data.answer || "",

                sources:
                    data.sources || [],

                level:
                    level,
            };


            setMessages(
                (previousMessages) => [

                    ...previousMessages,

                    assistantMessage,

                ]
            );


        } catch (err) {

            console.error(
                "Chat error:",
                err
            );


            setError(
                err.message ||
                "Something went wrong."
            );


        } finally {

            setLoading(false);

        }

    };


    /* =========================================
       COPY ANSWER
    ========================================= */

    const copyAnswer = async (
        text,
        index
    ) => {

        try {

            await navigator.clipboard.writeText(
                text
            );


            setCopiedIndex(index);


            setTimeout(() => {

                setCopiedIndex(null);

            }, 2000);


        } catch (err) {

            console.error(
                "Copy failed:",
                err
            );

        }

    };


    /* =========================================
       CLEAR CHAT
    ========================================= */

    const clearChat = () => {

        const confirmed =
            window.confirm(
                "Clear the entire chat?"
            );


        if (confirmed) {

            setMessages([]);

            setQuestion("");

            setError("");

            setCopiedIndex(null);

        }

    };


    /* =========================================
       SOURCE RENDER
    ========================================= */

    const renderSources = (
        sources
    ) => {

        if (
            !sources ||
            sources.length === 0
        ) {
            return null;
        }


        return (

            <div className="chat-sources">

                <div className="chat-sources-title">

                    <FaBook />

                    <span>
                        FMT Material Used
                    </span>

                </div>


                {sources.map(
                    (
                        source,
                        index
                    ) => {


                        if (
                            typeof source ===
                            "string"
                        ) {

                            return (

                                <div
                                    className="chat-source-item"
                                    key={index}
                                >

                                    <strong>
                                        {source}
                                    </strong>

                                </div>

                            );

                        }


                        return (

                            <div
                                className="chat-source-item"
                                key={index}
                            >

                                <strong>
                                    {source.source ||
                                        "Unknown source"}
                                </strong>


                                {source.chunk !==
                                    undefined && (

                                    <span>

                                        {" "}
                                        • Chunk{" "}

                                        {source.chunk}

                                    </span>

                                )}

                            </div>

                        );

                    }
                )}

            </div>

        );

    };


    return (

        <div className="chatbox">


            {/* =========================================
               CHAT HEADER
            ========================================= */}

            <div className="chat-header">

                <div className="chat-title">

                    <div className="chat-title-icon">

                        <FaRobot />

                    </div>


                    <div>

                        <h2>
                            FMT Assistant
                        </h2>

                        <p>
                            {level === "UG"
                                ? "Undergraduate"
                                : "Postgraduate"}
                            {" • "}
                            Exam-oriented FMT learning
                        </p>

                    </div>

                </div>


                {messages.length > 0 && (

                    <button
                        type="button"
                        className="clear-chat-button"
                        onClick={clearChat}
                        disabled={loading}
                    >

                        <FaTrash />

                        Clear Chat

                    </button>

                )}

            </div>



            {/* =========================================
               LEVEL SELECTOR
            ========================================= */}

            <div className="level-selector">

                <span>
                    Answer level:
                </span>


                <button
                    type="button"

                    onClick={() =>
                        setLevel("UG")
                    }

                    className={
                        level === "UG"
                            ? "active"
                            : ""
                    }

                    disabled={loading}
                >
                    UG
                </button>


                <button
                    type="button"

                    onClick={() =>
                        setLevel("PG")
                    }

                    className={
                        level === "PG"
                            ? "active"
                            : ""
                    }

                    disabled={loading}
                >
                    PG
                </button>

            </div>



            {/* =========================================
               MESSAGES
            ========================================= */}

            <div className="messages-container">


                {/* =====================================
                   EMPTY CHAT
                ===================================== */}

                {messages.length === 0 &&
                    !loading && (

                        <div className="empty-chat">

                            <div className="empty-chat-icon">

                                <FaRobot />

                            </div>


                            <h2>
                                How can I help you?
                            </h2>


                            <p>

                                Ask any Forensic
                                Medicine and Toxicology
                                question. Answers are
                                generated using your FMT
                                knowledge base.

                            </p>


                            <div className="suggested-questions">

                                <div className="suggested-questions-title">

                                    Suggested questions

                                </div>


                                {suggestedQuestions.map(
                                    (
                                        suggestedQuestion,
                                        index
                                    ) => (

                                        <button
                                            key={index}

                                            type="button"

                                            className="suggested-question"

                                            onClick={() =>
                                                askQuestion(
                                                    suggestedQuestion
                                                )
                                            }
                                        >

                                            {
                                                suggestedQuestion
                                            }

                                        </button>

                                    )
                                )}

                            </div>

                        </div>

                    )}



                {/* =====================================
                   CHAT HISTORY
                ===================================== */}

                {messages.map(
                    (
                        message,
                        index
                    ) => (

                        <React.Fragment
                            key={index}
                        >

                            <div
                                className={
                                    `message-row ${message.type}`
                                }
                            >


                                {/* USER */}

                                {message.type ===
                                    "user" && (

                                    <>

                                        <div className="message-label">

                                            You

                                        </div>


                                        <div className="message-bubble user-message">

                                            {
                                                message.content
                                            }

                                        </div>


                                        <div className="message-avatar user-avatar">

                                            <FaUser />

                                        </div>

                                    </>

                                )}



                                {/* AI */}

                                {message.type ===
                                    "assistant" && (

                                    <>

                                        <div className="message-avatar assistant-avatar">

                                            <FaRobot />

                                        </div>


                                        <div className="assistant-message-wrapper">

                                            <div className="message-label">

                                                FMT Assistant
                                                {" • "}
                                                {
                                                    message.level
                                                }

                                            </div>


                                            <div className="message-bubble assistant-message">

                                                <div className="message-markdown">

                                                    <ReactMarkdown
                                                        remarkPlugins={[
                                                            remarkGfm,
                                                        ]}
                                                    >

                                                        {
                                                            message.content
                                                        }

                                                    </ReactMarkdown>

                                                </div>


                                                <div className="message-actions">

                                                    <button
                                                        type="button"

                                                        className={
                                                            `copy-answer-button ${
                                                                copiedIndex ===
                                                                index
                                                                    ? "copied"
                                                                    : ""
                                                            }`
                                                        }

                                                        onClick={() =>
                                                            copyAnswer(
                                                                message.content,
                                                                index
                                                            )
                                                        }
                                                    >

                                                        {copiedIndex ===
                                                        index ? (

                                                            <>

                                                                <FaCheck />

                                                                Copied

                                                            </>

                                                        ) : (

                                                            <>

                                                                <FaCopy />

                                                                Copy Answer

                                                            </>

                                                        )}

                                                    </button>

                                                </div>

                                            </div>

                                        </div>

                                    </>

                                )}

                            </div>


                            {/* SOURCES */}

                            {message.type ===
                                "assistant" &&
                                renderSources(
                                    message.sources
                                )}

                        </React.Fragment>

                    )
                )}



                {/* =====================================
                   LOADING
                ===================================== */}

                {loading && (

                    <div className="message-row assistant">

                        <div className="message-avatar assistant-avatar">

                            <FaRobot />

                        </div>


                        <div className="message-bubble assistant-message">

                            <div className="thinking-message">

                                <div className="thinking-dots">

                                    <span></span>

                                    <span></span>

                                    <span></span>

                                </div>


                                <span className="thinking-text">

                                    Searching FMT material
                                    and generating answer...

                                </span>

                            </div>

                        </div>

                    </div>

                )}



                {/* =====================================
                   ERROR
                ===================================== */}

                {error && (

                    <div className="chat-error">

                        {error}

                    </div>

                )}

            </div>



            {/* =========================================
               INPUT
            ========================================= */}

            <div className="input-area">

                <input
                    type="text"

                    placeholder={
                        `Ask your ${level} FMT question...`
                    }

                    value={question}

                    disabled={loading}

                    onChange={(e) =>
                        setQuestion(
                            e.target.value
                        )
                    }

                    onKeyDown={(e) => {

                        if (
                            e.key === "Enter" &&
                            !e.shiftKey
                        ) {

                            e.preventDefault();

                            askQuestion();

                        }

                    }}
                />


                <button
                    type="button"

                    onClick={() =>
                        askQuestion()
                    }

                    disabled={
                        loading ||
                        !question.trim()
                    }
                >

                    {loading ? (

                        "..."

                    ) : (

                        <FaPaperPlane />

                    )}

                </button>

            </div>

        </div>

    );

}

export default ChatBox;