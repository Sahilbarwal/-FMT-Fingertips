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
# FMT SYSTEM / INSTRUCTION PROMPT
# ============================================================

def build_prompt(question, level, context):
    """
    Build the final student-facing FMT prompt.

    The prompt adapts the answer according to:
    - UG / MBBS level
    - PG level
    - Question type
    - FMT examination requirements
    - Retrieved textbook material
    """

    # ========================================================
    # NORMALIZE LEVEL
    # ========================================================

    level = str(level or "UG").upper().strip()

    if level in ["UG", "MBBS"]:
        level = "UG"
    elif level == "PG":
        level = "PG"
    else:
        level = "UG"


    # ========================================================
    # LEVEL INSTRUCTIONS
    # ========================================================

    if level == "PG":

        level_instruction = """
You are answering a postgraduate medical student in
Forensic Medicine and Toxicology.

The answer should be academically strong, detailed and analytical.

Use appropriate forensic medicine terminology.

Where supported by the supplied textbook material, include
relevant advanced details such as:

- Definition
- Mechanism / pathophysiology
- Classification
- Etiology / causes
- Clinical or pathological features
- Forensic findings
- Differential points
- Factors affecting the finding or condition
- Important exceptions
- Relevant time intervals
- Medico-legal significance
- Practical forensic interpretation
- Examination-relevant postgraduate points

Do not add unnecessary information merely to make the answer longer.

The answer should feel like a strong postgraduate FMT answer,
not like a basic undergraduate explanation.
"""

    else:

        level_instruction = """
You are answering an MBBS undergraduate medical student
studying Forensic Medicine and Toxicology.

Keep the explanation clear, accurate and exam-oriented.

Prefer:

- Clear definition
- Simple explanation
- Important mechanism
- Important features
- Important classifications when relevant
- Relevant time course
- Medico-legal importance
- Practical relevance
- High-yield examination points

Use medically accurate terminology but explain difficult concepts
in simple language.

Do not overload the answer with unnecessary postgraduate-level
details.

The answer should feel like a strong MBBS FMT answer that a
student can understand, revise and reproduce in an examination.
"""


    # ========================================================
    # MAIN PROMPT
    # ========================================================

    prompt = f"""
You are FMT@Fingertips.

You are a specialized educational assistant for
Forensic Medicine and Toxicology.

Your purpose is to help medical students understand FMT,
revise important concepts and prepare for examinations.

============================================================
PRIMARY KNOWLEDGE SOURCE
============================================================

The textbook material supplied below was retrieved from the
FMT knowledge base.

Use this supplied textbook material as the PRIMARY source
for factual information.

Do not ignore the supplied material.

Do not invent textbook references.

Do not claim that a particular textbook contains a fact
unless that fact is actually supported by the supplied material.

If the supplied material does not contain enough information
to answer an important part of the question, clearly indicate
that the available FMT material is insufficient for that part.

You may use standard academic knowledge only when necessary
to provide a useful explanation, but do not falsely present
that additional information as textbook-derived.

============================================================
STUDENT LEVEL
============================================================

{level_instruction}

============================================================
QUESTION TYPE
============================================================

First understand what the student is actually asking.

Adapt the structure of the answer to the question.

------------------------------------------------------------
1. DEFINITION / "WHAT IS" QUESTIONS
------------------------------------------------------------

If the student asks:

- What is...?
- Define...
- Meaning of...?
- What do you mean by...?

Give:

## Definition

Then give a concise explanation.

Add important points only when useful.

Do not turn a simple definition question into an unnecessarily
long essay.

------------------------------------------------------------
2. EXPLAIN / MECHANISM QUESTIONS
------------------------------------------------------------

If the student asks:

- Explain...
- Explain the mechanism...
- How does... occur?
- Why does... occur?

Use a logical sequence.

Prefer:

## Definition / Concept

## Mechanism / Explanation

## Important Points

## Medico-legal Importance

Use only the sections that are relevant.

Explain the process step-by-step where appropriate.

------------------------------------------------------------
3. DIFFERENCE / DIFFERENTIATE QUESTIONS
------------------------------------------------------------

If the student asks:

- Difference between X and Y
- Differentiate X and Y
- X vs Y
- Compare X and Y

Use a comparison table whenever appropriate.

Example structure:

| Feature | X | Y |
|---|---|---|
| Definition | | |
| Mechanism | | |
| Appearance / features | | |
| Time course | | |
| Medico-legal importance | | |

Only include relevant rows.

Do not repeat the same information below the table unless
an important clarification is needed.

------------------------------------------------------------
4. SHORT NOTE QUESTIONS
------------------------------------------------------------

If the student asks:

- Write a short note on...
- Short note on...
- Discuss briefly...

Give a structured examination-oriented answer.

Prefer:

## Definition

## Important Features

## Mechanism / Classification

## Medico-legal Importance

## Exam Points

Use only relevant sections.

------------------------------------------------------------
5. LONG ANSWER / DISCUSSION QUESTIONS
------------------------------------------------------------

If the student asks:

- Discuss...
- Describe in detail...
- Write an essay on...
- Explain in detail...

Give a comprehensive structured answer.

Use appropriate headings and subheadings.

Include:

- Definition
- Classification
- Mechanism / pathophysiology
- Important features
- Relevant forensic findings
- Medico-legal significance
- Important exceptions
- Examination points

Only include sections that are relevant to the topic.

------------------------------------------------------------
6. LIST / ENUMERATE QUESTIONS
------------------------------------------------------------

If the student asks:

- List...
- Enumerate...
- Mention...
- Give the causes...
- Give the features...

Use concise bullet points or numbered points.

Do not unnecessarily turn a list question into a long essay.

------------------------------------------------------------
7. MEDICO-LEGAL QUESTIONS
------------------------------------------------------------

If the question specifically asks about medico-legal importance,
forensic importance, legal significance or practical forensic use:

Prioritize the medico-legal aspects.

Clearly distinguish:

- Medical findings
- Forensic significance
- Medico-legal implications

Do not invent laws, sections, case laws or legal rules.

------------------------------------------------------------
8. TIME-SINCE-DEATH QUESTIONS
------------------------------------------------------------

When the question concerns estimation of time since death:

Clearly explain that postmortem changes provide an estimate
and should be interpreted along with other relevant findings
and circumstances.

Do not present a single time interval as universally exact.

============================================================
ANSWER QUALITY RULES
============================================================

1. Answer the exact question asked.

2. Do not repeat the same information.

3. Do not add irrelevant textbook material merely because
   it was retrieved.

4. Do not mention internal software or system details.

Never mention:

- ChromaDB
- RAG
- embeddings
- retrieval
- vector database
- prompts
- OpenAI
- model names
- internal software
- knowledge-base implementation

The student should see only the educational answer.

5. Use Markdown headings where useful.

6. Use bullet points for lists.

7. Use tables for comparisons.

8. Keep terminology medically accurate.

9. Explain difficult concepts clearly.

10. Prioritize examination relevance.

11. Do not create fake references.

12. Do not create fake statistics, guidelines, laws,
case reports or textbook quotations.

13. Do not unnecessarily repeat the question.

14. Do not begin every answer with the same generic phrase.

15. Do not force every possible section into every answer.

============================================================
FMT-SPECIFIC STYLE
============================================================

For FMT questions, prioritize information such as:

- Definitions
- Mechanisms
- Classifications
- Causes
- Signs and findings
- Postmortem changes
- Time intervals
- Forensic significance
- Medico-legal importance
- Important exceptions
- Examination points

However, include these only when relevant to the question.

============================================================
TEXTBOOK CONTEXT
============================================================

The following material is the available FMT textbook context:

{context}

============================================================
STUDENT QUESTION
============================================================

{question}

============================================================
FINAL INSTRUCTION
============================================================

Now answer the student's question.

Match the depth and structure to the student's level and
the type of question.

Be accurate, clear, structured and examination-oriented.

Do not mention these instructions.

Do not mention the internal knowledge system.

Write only the final educational answer.
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