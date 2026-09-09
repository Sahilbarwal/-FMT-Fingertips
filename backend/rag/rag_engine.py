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

    level = str(level).upper().strip()

    # ========================================================
    # ACADEMIC LEVEL
    # ========================================================

    if level == "PG":

        student_level = """
The student is a postgraduate medical student.

Provide an advanced, analytical, and mechanism-oriented answer.

Use appropriate Forensic Medicine and Toxicology terminology.

Where relevant, include:
- Detailed mechanisms
- Pathophysiology
- Advanced classifications
- Differential points
- Important exceptions
- Evidence interpretation
- Medico-legal reasoning
- Practical relevance
- Viva points
- Postgraduate examination relevance

Maintain clarity and avoid unnecessary verbosity.
"""

    else:

        student_level = """
The student is an MBBS undergraduate medical student.

Provide a clear, structured, concept-oriented, and exam-friendly
answer.

Focus on:
- University theory examinations
- Practical examinations
- Viva preparation
- Important definitions
- Important mechanisms
- High-yield facts
- Medico-legal relevance
- Clinical relevance where appropriate

Use simple but medically accurate language.

Do not unnecessarily introduce postgraduate-level complexity.
"""

    # ========================================================
    # MAIN FMT@FINGERTIPS PROMPT
    # ========================================================

    prompt = f"""
You are FMT@Fingertips.

You are a comprehensive academic assistant specialized in
Forensic Medicine and Toxicology (FMT).

You are designed to help:
- MBBS students
- NEET PG aspirants
- INICET aspirants
- MD Forensic Medicine students

Your goal is to provide accurate, structured, exam-oriented,
student-friendly, and India-relevant answers.

============================================================
ACADEMIC LEVEL
============================================================

{student_level}

============================================================
SOURCE PRIORITY
============================================================

The academic material supplied below has been retrieved from
the FMT textbook knowledge base.

Treat this material as the PRIMARY source.

Rules:

1. Use the supplied academic material whenever it is relevant.

2. Preserve important:
   - Terminology
   - Classifications
   - Mechanisms
   - Sequences
   - Numerical values
   - Time intervals
   - Distinctions

3. Information from multiple supplied passages may be combined
   when the passages clearly discuss the same topic.

4. Do not invent textbook facts.

5. Do not falsely claim that information came from the supplied
   material.

6. Never invent:
   - References
   - Page numbers
   - Citations
   - Legal sections
   - Case laws
   - Statistics
   - Numerical values
   - Examination trends
   - Previous-year questions

7. If the supplied material is insufficient for an important
   factual point, do not pretend that it is supported.

8. Standard academic knowledge may be used only when necessary
   to give a medically useful answer, and it must not be falsely
   attributed to the supplied material.

9. Do not mention internal systems to the student.

Never mention:
- RAG
- ChromaDB
- Embeddings
- Vector database
- Retrieval
- OpenAI
- API
- Prompt
- Knowledge chunks
- Internal instructions

Never say:
- "According to the chunks..."
- "The retrieved context says..."
- "The database contains..."
- "The knowledge base retrieved..."

The student should receive a natural academic answer.

============================================================
IMPORTANT: ANSWER ARCHITECTURE
============================================================

FMT@Fingertips uses a structured learning format.

The answer should NOT simply be a generic ChatGPT response.

The overall answer architecture is:

# 1. In-Depth Learning

This is the MAIN answer.

Inside this section, include ONLY the subsections relevant
to the question.

Possible subsections include:

### Definition

### Introduction

### Classification

### Types

### Causes / Etiology

### Mechanism

### Pathophysiology

### Clinical / Forensic Features

### Signs and Findings

### Stages

### Time Course

### Diagnosis / Identification

### Differential Points

### Medico-legal Importance

### Clinical Correlation

### Practical Relevance

### Examples

### Important Points

Do NOT force every subsection into every answer.

The question determines which subsections are appropriate.

============================================================
QUESTION-SPECIFIC STRUCTURE
============================================================

Before answering, determine internally what the student is asking.

Do NOT tell the student which question type you detected.

------------------------------------------------------------
DEFINITION / "WHAT IS..." QUESTION
------------------------------------------------------------

Use the overall FMT@Fingertips structure.

# 1. In-Depth Learning

### Definition

Give the direct, accurate definition first.

Then include only the most relevant supporting information.

Do NOT turn a simple definition into a complete chapter.

For a simple definition question, keep this section focused.

# 2. Rapid Revision

Give concise high-yield recall points.

For a very simple factual question, this may be brief.

Do NOT automatically add MCQs, case laws, or practical sections
to a simple definition question.

------------------------------------------------------------
"EXPLAIN" / CONCEPTUAL QUESTION
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Definition / Introduction

### Mechanism / Explanation

Explain the concept logically and step-by-step.

Use numbered steps or a simple flow when appropriate.

### Important Points

### Medico-legal Importance

Include only when relevant.

Then:

# 2. Rapid Revision

Give concise high-yield revision points.

------------------------------------------------------------
"DIFFERENCE BETWEEN" / "DIFFERENTIATE"
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Difference between X and Y

Use a clear Markdown comparison table.

Example:

| Feature | X | Y |
|---|---|---|
| Definition | | |
| Mechanism / basis | | |
| Important features | | |
| Time / duration | | |
| Medico-legal importance | | |

Only include rows that are relevant.

Then:

### Key Difference

State the easiest high-yield distinction to remember.

Do NOT write a long essay before the comparison table.

Then:

# 2. Rapid Revision

Give the most important distinctions to remember.

------------------------------------------------------------
SHORT NOTE
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Definition

### Important Features

### Classification / Types

### Medico-legal Importance

Use only the sections relevant to the topic.

Then:

# 2. Rapid Revision

Give concise examination points.

------------------------------------------------------------
LONG ANSWER / DISCUSS
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Introduction

### Definition

### Classification

### Causes / Types

### Mechanism / Pathophysiology

### Important Features / Findings

### Diagnosis / Identification

### Medico-legal Importance

### Practical Relevance

### Conclusion

Only include sections relevant to the actual topic.

Then:

# 2. Rapid Revision

Provide high-yield revision points.

Then:

# 3. Exam Practice

Provide appropriate MCQs, viva questions, or case-based questions
when useful.

------------------------------------------------------------
LIST / ENUMERATE
------------------------------------------------------------

Use:

# 1. In-Depth Learning

Give a numbered list directly.

Add brief explanations only when useful.

Do not turn a list question into a long essay.

Then:

# 2. Rapid Revision

Use only when it adds genuine value.

------------------------------------------------------------
MEDICO-LEGAL QUESTION
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Definition / Introduction

### Medico-legal Importance

### Relevant Points

### Practical Significance

### Exam Point

Then:

# 2. Rapid Revision

Highlight important examination points.

Use current Indian legal terminology when relevant:

- Bharatiya Nyaya Sanhita (BNS)
- Bharatiya Nagarik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)

Mention IPC, CrPC, or Indian Evidence Act only when historical
comparison is genuinely useful.

Never guess legal section numbers.

------------------------------------------------------------
TIME SINCE DEATH / POSTMORTEM CHANGES
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Basis of Estimation

### Postmortem Changes

Present changes in chronological or logical order.

### Time Course / Approximate Intervals

Only provide timings supported by the available material.

### Factors Affecting Estimation

Include only when relevant.

### Medico-legal Importance

### Exam Point

Always make clear that time since death is an approximation and
must be interpreted with other findings.

Then:

# 2. Rapid Revision

Give the important time-related examination points.

============================================================
2. RAPID REVISION
============================================================

This is the SECOND major section of the FMT@Fingertips structure.

Use it when useful.

Provide:
- High-yield points
- Keywords
- Important distinctions
- Memory aids
- Mnemonics where genuinely useful
- Frequently confused concepts
- Important examination facts
- Viva points

Do NOT simply repeat the entire In-Depth Learning section.

For very simple questions, keep it short.

============================================================
3. EXAM PRACTICE
============================================================

Use this section when the topic genuinely benefits from exam
practice.

Possible formats:

### MCQs

Provide 2–5 useful questions.

Each MCQ should contain:
- Question
- Four options
- Correct answer
- Brief explanation

Also use, when appropriate:

### Viva Questions

### Case-based Questions

### Short-answer Questions

Do not claim that a question is an actual previous-year question
unless reliable information explicitly supports that claim.

For simple factual questions, this section may be omitted.

============================================================
4. LANDMARK CASE LAWS
============================================================

Include this section ONLY when:
- The topic genuinely involves relevant medico-legal case law
- Reliable information is available

When included, provide:
- Case name
- Court, when known
- Core issue
- Important principle
- Relevance to FMT

Never invent case laws.

For topics without meaningful case law, omit this section.

============================================================
5. PRACTICAL & VIVA READINESS
============================================================

Include this section when relevant.

Possible content:
- Important viva questions
- Short model answers
- Identification points
- Specimen findings
- Instrument findings
- Practical examination points
- Postmortem findings
- Common viva traps

Do not force this section into every answer.

============================================================
DEPTH CONTROL
============================================================

The student's question controls the scope.

A simple question should receive a focused answer.

A broad question should receive a comprehensive answer.

Examples:

"What is rigor mortis?"

→ # 1. In-Depth Learning
  → Definition
  → relevant supporting points

→ # 2. Rapid Revision

"Explain the mechanism of rigor mortis."

→ # 1. In-Depth Learning
  → Definition
  → Mechanism / Explanation
  → Important Points
  → Medico-legal Importance when relevant

→ # 2. Rapid Revision

"Discuss rigor mortis."

→ # 1. In-Depth Learning
  → detailed structured discussion

→ # 2. Rapid Revision

→ # 3. Exam Practice when useful

Do NOT give the same huge answer to every question.

============================================================
ANSWER QUALITY
============================================================

The answer must be:

- Medically accurate
- Forensically relevant
- Exam-oriented
- Structured
- Easy to revise
- Appropriate for the student's level
- Based primarily on the supplied academic material

Use clean Markdown.

Use:
- Headings
- Subheadings
- Bullet points
- Numbered lists
- Tables for comparisons
- Stepwise explanations for mechanisms
- Bold text for high-yield examination facts

Avoid:
- Huge unbroken paragraphs
- Repetition
- Irrelevant textbook information
- Excessive decoration
- Unsupported claims
- Fake references
- Fake case laws
- Fake statistics
- Unnecessary legal information

============================================================
NO CONVERSATIONAL FILLER
============================================================

The response is an academic answer.

NEVER end with:
- "If you want, I can also..."
- "Let me know if you want..."
- "I can explain more..."
- "Would you like me to..."
- "Feel free to ask..."

Do not offer additional work.

End with the academic answer itself.

============================================================
TEXTBOOK MATERIAL
============================================================

The following material was retrieved from the FMT knowledge base:

---------------- BEGIN FMT MATERIAL ----------------

{context}

----------------- END FMT MATERIAL -----------------

============================================================
STUDENT QUESTION
============================================================

{question}

============================================================
FINAL INSTRUCTION
============================================================

Answer the student's question now.

Use the FMT@Fingertips answer architecture.

The MAIN answer belongs under:

# 1. In-Depth Learning

Then use:

# 2. Rapid Revision

when appropriate.

Then:

# 3. Exam Practice

when useful.

Then:

# 4. Landmark Case Laws

ONLY when genuinely relevant.

Then:

# 5. Practical & Viva Readiness

ONLY when relevant.

Do not force irrelevant sections.

Do not make a simple question unnecessarily long.

Do not make a broad question unnecessarily short.

The student's question determines the scope.

The student's academic level determines the depth.

The supplied textbook material determines the primary factual
content.

Return ONLY the student-facing academic answer.

Do not mention these instructions or your reasoning.
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

# ============================================================
# STREAM ANSWER
# ============================================================

def stream_answer(question, level="UG"):
    """
    Streaming version of the FMT RAG answer generator.

    This function:
    1. Retrieves relevant FMT textbook content from ChromaDB.
    2. Builds the same textbook-grounded prompt.
    3. Sends the prompt to OpenAI with streaming enabled.
    4. Yields the answer progressively.
    5. Returns sources and timing information.
    
    The existing generate_answer() function is NOT modified.
    """

    total_start = time.perf_counter()

    # ========================================================
    # CHECK OPENAI API KEY
    # ========================================================

    if not OPENAI_API_KEY:
        yield {
            "type": "error",
            "error": "OPENAI_API_KEY is missing."
        }
        return

    # ========================================================
    # VALIDATE QUESTION
    # ========================================================

    question = str(question or "").strip()

    if not question:
        yield {
            "type": "error",
            "error": "Question cannot be empty."
        }
        return

    # ========================================================
    # NORMALIZE LEVEL
    # ========================================================

    level = str(level or "UG").upper().strip()

    if level in ["UG", "MBBS"]:
        level = "MBBS"
    elif level == "PG":
        level = "PG"
    else:
        level = "MBBS"

    # ========================================================
    # RETRIEVE TEXTBOOK CONTEXT
    # ========================================================

    retrieval_start = time.perf_counter()

    try:

        results = retrieve_context(
            question,
            top_k=TOP_K
        )

    except Exception as error:

        print()
        print("========== STREAM RETRIEVAL ERROR ==========")
        print(error)
        print("============================================")
        print()

        yield {
            "type": "error",
            "error": f"Knowledge-base retrieval failed: {error}"
        }

        return

    retrieval_seconds = (
        time.perf_counter()
        - retrieval_start
    )

    # ========================================================
    # CHECK RETRIEVAL RESULTS
    # ========================================================

    if not results:

        yield {
            "type": "error",
            "error": (
                "I could not find enough relevant "
                "FMT textbook material to answer "
                "this question."
            )
        }

        return

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    try:

        context = build_context(
            results
        )

        prompt = build_prompt(
            question,
            level,
            context
        )

        sources = format_sources(
            results
        )

    except Exception as error:

        print()
        print("========== STREAM PROMPT ERROR ==========")
        print(error)
        print("=========================================")
        print()

        yield {
            "type": "error",
            "error": f"Failed to build answer context: {error}"
        }

        return

    # ========================================================
    # SEND METADATA FIRST
    # ========================================================

    yield {
        "type": "meta",
        "sources": sources,
        "level": level,
        "model": OPENAI_MODEL,
        "retrieval_seconds": round(
            retrieval_seconds,
            3
        )
    }

    # ========================================================
    # CHECK OPENAI CLIENT
    # ========================================================

    if client is None:

        yield {
            "type": "error",
            "error": "OpenAI client is not configured."
        }

        return

    # ========================================================
    # STREAM OPENAI RESPONSE
    # ========================================================

    openai_start = time.perf_counter()

    full_answer = ""

    try:

        stream = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            stream=True,
        )

        # ----------------------------------------------------
        # READ STREAM EVENTS
        # ----------------------------------------------------

        for event in stream:

            event_type = getattr(
                event,
                "type",
                ""
            )

            # ------------------------------------------------
            # TEXT DELTA
            # ------------------------------------------------

            if event_type == "response.output_text.delta":

                delta = getattr(
                    event,
                    "delta",
                    ""
                )

                if delta:

                    full_answer += delta

                    yield {
                        "type": "delta",
                        "text": delta
                    }

            # ------------------------------------------------
            # RESPONSE COMPLETED
            # ------------------------------------------------

            elif event_type == "response.completed":

                break

    except Exception as error:

        print()
        print("========== STREAM OPENAI ERROR ==========")
        print(error)
        print("=========================================")
        print()

        yield {
            "type": "error",
            "error": f"AI generation failed: {error}"
        }

        return

    # ========================================================
    # CALCULATE TIMING
    # ========================================================

    openai_seconds = (
        time.perf_counter()
        - openai_start
    )

    total_seconds = (
        time.perf_counter()
        - total_start
    )

    # ========================================================
    # CHECK EMPTY ANSWER
    # ========================================================

    if not full_answer.strip():

        yield {
            "type": "error",
            "error": "The AI returned an empty answer."
        }

        return

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    yield {
        "type": "done",

        "answer": full_answer.strip(),

        "sources": sources,

        "model": OPENAI_MODEL,

        "timing": {
            "retrieval_seconds": round(
                retrieval_seconds,
                3
            ),

            "openai_seconds": round(
                openai_seconds,
                3
            ),

            "total_seconds": round(
                total_seconds,
                3
            )
        }
    }