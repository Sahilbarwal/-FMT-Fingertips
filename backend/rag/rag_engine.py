import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .retriever import retrieve_context


# ============================================================
# PATHS / ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# Load backend/.env
load_dotenv(
    BASE_DIR.parent / ".env"
)


# ============================================================
# OPENAI SETTINGS
# ============================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.4-nano"
)


# ============================================================
# RAG SETTINGS
# ============================================================

# Number of ChromaDB chunks retrieved
TOP_K = 8


# ============================================================
# OPENAI CLIENT
# ============================================================

client = None

if OPENAI_API_KEY:

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(results):
    """
    Convert retrieved ChromaDB results into a clean
    context block for the OpenAI model.
    """

    if not results:

        return (
            "No relevant FMT textbook material "
            "was retrieved."
        )

    context_blocks = []

    for index, item in enumerate(
        results,
        start=1
    ):

        source = item.get(
            "source",
            "Unknown source"
        )

        chunk = item.get(
            "chunk",
            "Unknown"
        )

        text = item.get(
            "text",
            ""
        )

        context_blocks.append(
            f"""
============================================================
SOURCE {index}
============================================================

TEXTBOOK:
{source}

CHUNK:
{chunk}

CONTENT:
{text}
"""
        )

    return "\n".join(
        context_blocks
    )


# ============================================================
# SYSTEM / INSTRUCTION PROMPT
# ============================================================
def build_prompt(question, level, context):

    level_instruction = """
You are answering for an MBBS undergraduate medical student.

Explain concepts clearly, simply, and in an exam-oriented manner.
Start with the core concept and then add relevant detail.
Use simple language while maintaining medical accuracy.
Focus on important definitions, mechanisms, features, medico-legal
importance, practical relevance, and high-yield examination points.
"""
    
    if level == "PG":
        level_instruction = """
You are answering for a postgraduate medical student.

Provide a detailed, analytical, and advanced answer.
Include mechanisms, pathophysiology, differential points,
advanced medico-legal reasoning, important controversies,
and postgraduate entrance examination relevance where appropriate.
"""

    prompt = f"""
You are FMT@Fingertips, a comprehensive academic assistant for
Forensic Medicine and Toxicology.

Your primary purpose is to help MBBS students and postgraduate
medical students study Forensic Medicine and Toxicology in a clear,
structured, detailed, exam-oriented, and India-specific manner.

====================================================
PRIMARY SOURCE RULE
====================================================

The FMT study material provided below was retrieved from the user's
knowledge base.

Use this retrieved material as the PRIMARY source for answering the
question.

Do not ignore the retrieved material.

Do not invent citations or claim that a source says something it does
not say.

If the retrieved material is insufficient to fully answer the question,
you may supplement it with standard academic knowledge, but do not
falsely claim that the additional information came from the retrieved
material.

The retrieved material controls WHAT factual information should be
used.

The instructions below control HOW the answer should be presented.

====================================================
LEARNING LEVEL
====================================================

{level_instruction}

====================================================
ANSWER DEPTH
====================================================

Do not give an unnecessarily short answer.

For a simple factual question:
Give a concise but complete answer with the important explanation.

For a conceptual question:
Provide a detailed explanation.

For questions involving exam preparation, detailed notes, mechanisms,
medico-legal importance, practicals, viva, or postgraduate learning:
Provide a comprehensive answer.

Always answer the user's actual question first.

Do not force unnecessary sections if they are not relevant.

====================================================
RESPONSE FORMAT
====================================================

When appropriate, structure the answer using the following sections.

# 1. In-Depth Learning

Provide a detailed and logically structured explanation.

Include relevant points such as:

- Definition
- Classification
- Mechanism
- Pathophysiology
- Important features
- Stages
- Causes
- Signs and findings
- Medico-legal importance
- Clinical correlation
- Practical correlation
- Examples
- Important differentiating points

For Indian medico-legal topics, use current Indian legal terminology
when relevant:

- Bharatiya Nyaya Sanhita (BNS)
- Bharatiya Nagarik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)

Mention IPC, CrPC, or Indian Evidence Act only when historical
comparison is useful.

Do not force legal information when unrelated to the question.

# 2. Rapid Revision

Provide concise, high-yield revision points.

Use:

- Bullet points
- Important keywords
- Memory aids
- Mnemonics where useful
- Frequently confused concepts
- High-yield facts
- Important viva points

Make this useful for last-minute revision.

# 3. Exam Practice

When relevant, provide 2 to 5 exam-style MCQs.

Each MCQ should include:

- Question
- Options
- Correct answer
- Brief explanation

Make them suitable for MBBS, NEET PG, INICET, or postgraduate
entrance preparation.

Do not falsely claim that a question appeared in an actual exam.

# 4. Landmark Case Laws

Include this section ONLY when the topic genuinely has relevant
medico-legal case law.

For each case include:

- Case name
- Court if known
- Core issue
- Important principle
- Relevance to forensic medicine

Never invent case laws.

# 5. Practical and Viva Readiness

Include only relevant practical preparation such as:

- Important viva questions
- Short model answers
- Identification points
- Instrument or specimen points
- Postmortem findings
- Certificate-related points
- Injury examination
- Death examination
- Drunkenness examination
- Poisoning examination
- Practical tips

# 6. Visual Aid

When useful, provide:

- Comparison tables
- Flowcharts
- Stepwise mechanisms
- Text diagrams

Example:

Death
↓
Primary flaccidity
↓
ATP depletion
↓
Actin-myosin fixation
↓
Rigor mortis

Keep visual aids simple and easy to memorize.

# 7. Latest Updates and Exam Relevance

Include this ONLY when reliable and relevant information is available.

Do not claim something is "latest" or "recent" without reliable
support.

Do not invent exam trends, government notifications, legal updates,
or recent case laws.

# 8. References

For substantial answers, end with a References section.

Prioritize the retrieved FMT material.

You may also mention genuinely relevant standard references such as:

- Reddy and Murty's Essentials of Forensic Medicine and Toxicology
- Modi's Medical Jurisprudence and Toxicology
- Parikh's Forensic Medicine
- Knight's Forensic Pathology

Only include references genuinely relevant to the answer.

====================================================
COMMUNICATION STYLE
====================================================

Use:

- Clear headings
- Subheadings
- Bullet points
- Tables when useful
- Bold formatting for important terms
- Short paragraphs
- Comparison tables for confusing topics

Do not write one giant paragraph.

Maintain a professional, academic, student-friendly, neutral,
respectful, exam-oriented style.

Your goal is:

UNDERSTANDING + RETENTION + EXAM PERFORMANCE + PRACTICAL APPLICATION.

====================================================
RETRIEVED FMT KNOWLEDGE BASE MATERIAL
====================================================

{context}

====================================================
USER QUESTION
====================================================

{question}

Now provide the best possible answer based primarily on the retrieved
FMT material and present it in the appropriate FMT@Fingertips format.
"""

    return prompt


# ============================================================
# SOURCE INFORMATION
# ============================================================

def format_sources(results):
    """
    Prepare source information to send back to the frontend.

    This is separate from the actual AI answer.
    """

    sources = []

    seen = set()

    for item in results:

        source = item.get(
            "source",
            "Unknown source"
        )

        chunk = item.get(
            "chunk",
            "Unknown"
        )

        distance = item.get(
            "distance"
        )

        key = (
            source,
            chunk
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "source": source,
                "chunk": chunk,
                "distance": distance,
            }
        )

    return sources


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(
    question,
    level="MBBS"
):
    """
    Main RAG pipeline.

    Flow:

        Student Question
              ↓
        ChromaDB Retrieval
              ↓
        Relevant Textbook Chunks
              ↓
        Build Context
              ↓
        Build FMT Prompt
              ↓
        OpenAI
              ↓
        Structured FMT Answer
    """

    # ========================================================
    # VALIDATE API KEY
    # ========================================================

    if not OPENAI_API_KEY:

        return {
            "error":
                "OPENAI_API_KEY is missing. "
                "Add it to backend/.env.",

            "answer": "",

            "sources": [],

            "model": OPENAI_MODEL,

            "timing": None,
        }

    # ========================================================
    # VALIDATE QUESTION
    # ========================================================

    if not question:

        return {
            "error":
                "Question cannot be empty.",

            "answer": "",

            "sources": [],

            "model": OPENAI_MODEL,

            "timing": None,
        }

    question = str(
        question
    ).strip()

    if not question:

        return {
            "error":
                "Question cannot be empty.",

            "answer": "",

            "sources": [],

            "model": OPENAI_MODEL,

            "timing": None,
        }

    # ========================================================
    # VALIDATE LEVEL
    # ========================================================

    level = str(
        level
    ).upper().strip()

    # Backward compatibility:
    # UG = MBBS

    if level in [
        "UG",
        "MBBS"
    ]:

        level = "MBBS"

    elif level == "PG":

        level = "PG"

    else:

        level = "MBBS"

    # ========================================================
    # START TOTAL TIMER
    # ========================================================

    total_start = time.perf_counter()

    # ========================================================
    # RETRIEVAL
    # ========================================================

    retrieval_start = time.perf_counter()

    try:

        results = retrieve_context(
            question,
            top_k=TOP_K
        )

    except Exception as error:

        retrieval_seconds = (
            time.perf_counter()
            - retrieval_start
        )

        return {
            "error":
                "ChromaDB retrieval failed: "
                f"{error}",

            "answer": "",

            "sources": [],

            "model": OPENAI_MODEL,

            "timing": {
                "retrieval_seconds":
                    round(
                        retrieval_seconds,
                        3
                    ),

                "openai_seconds": 0,

                "total_seconds":
                    round(
                        retrieval_seconds,
                        3
                    ),
            },
        }

    retrieval_seconds = (
        time.perf_counter()
        - retrieval_start
    )

    # ========================================================
    # CHECK RETRIEVAL
    # ========================================================

    if not results:

        total_seconds = (
            time.perf_counter()
            - total_start
        )

        return {
            "error": None,

            "answer":
                (
                    "I could not find enough relevant "
                    "FMT material in the uploaded knowledge "
                    "base to answer this question accurately."
                ),

            "sources": [],

            "model": OPENAI_MODEL,

            "timing": {
                "retrieval_seconds":
                    round(
                        retrieval_seconds,
                        3
                    ),

                "openai_seconds": 0,

                "total_seconds":
                    round(
                        total_seconds,
                        3
                    ),
            },
        }

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context = build_context(
        results
    )

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = build_prompt(
        question,
        level,
        context
    )

    # ========================================================
    # OPENAI REQUEST
    # ========================================================

    openai_start = time.perf_counter()

    try:

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
        )

        answer = (
            response.output_text
            or ""
        ).strip()

    except Exception as error:

        openai_seconds = (
            time.perf_counter()
            - openai_start
        )

        total_seconds = (
            time.perf_counter()
            - total_start
        )

        return {
            "error":
                f"OpenAI API error: {error}",

            "answer": "",

            "sources":
                format_sources(
                    results
                ),

            "model": OPENAI_MODEL,

            "timing": {
                "retrieval_seconds":
                    round(
                        retrieval_seconds,
                        3
                    ),

                "openai_seconds":
                    round(
                        openai_seconds,
                        3
                    ),

                "total_seconds":
                    round(
                        total_seconds,
                        3
                    ),
            },
        }

    # ========================================================
    # OPENAI TIMER
    # ========================================================

    openai_seconds = (
        time.perf_counter()
        - openai_start
    )

    # ========================================================
    # CHECK EMPTY ANSWER
    # ========================================================

    if not answer:

        total_seconds = (
            time.perf_counter()
            - total_start
        )

        return {
            "error":
                "OpenAI returned an empty answer.",

            "answer": "",

            "sources":
                format_sources(
                    results
                ),

            "model": OPENAI_MODEL,

            "timing": {
                "retrieval_seconds":
                    round(
                        retrieval_seconds,
                        3
                    ),

                "openai_seconds":
                    round(
                        openai_seconds,
                        3
                    ),

                "total_seconds":
                    round(
                        total_seconds,
                        3
                    ),
            },
        }

    # ========================================================
    # TOTAL TIME
    # ========================================================

    total_seconds = (
        time.perf_counter()
        - total_start
    )

    # ========================================================
    # SOURCES
    # ========================================================

    sources = format_sources(
        results
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "error": None,

        "answer": answer,

        "sources": sources,

        "model": OPENAI_MODEL,

        "timing": {
            "retrieval_seconds":
                round(
                    retrieval_seconds,
                    3
                ),

            "openai_seconds":
                round(
                    openai_seconds,
                    3
                ),

            "total_seconds":
                round(
                    total_seconds,
                    3
                ),
        },
    }