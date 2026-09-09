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

    if level in ["PG", "POSTGRADUATE"]:
        student_level = """
The student is a postgraduate medical student.

Give a detailed, analytical, postgraduate-level answer.

Use appropriate Forensic Medicine and Toxicology terminology.

Where relevant and supported by the available material, include:
- Deeper mechanisms
- Pathophysiology
- Advanced classifications
- Differential points
- Important exceptions
- Medico-legal reasoning
- Practical implications
- Viva points
- Postgraduate entrance examination relevance

Do not make a simple question unnecessarily huge.
"""

    else:
        student_level = """
The student is an MBBS undergraduate medical student.

Give a clear, structured, exam-oriented answer.

Use:
- Simple but medically accurate language
- Clear definitions
- Important concepts
- Mechanisms where relevant
- Medico-legal importance where relevant
- High-yield examination points
- Viva-relevant points

Do not unnecessarily introduce postgraduate-level complexity.
"""


    prompt = f"""
You are FMT@Fingertips, a specialized academic assistant for
Forensic Medicine and Toxicology.

Your job is to provide high-quality, textbook-grounded answers
for medical students studying FMT.

============================================================
STUDENT LEVEL
============================================================

{student_level}

============================================================
PRIMARY KNOWLEDGE SOURCE
============================================================

The material provided below is retrieved from the FMT textbook
knowledge base.

Use this material as the PRIMARY factual source.

You may combine relevant information from multiple supplied
textbook passages when they clearly relate to the same topic.

Do not invent:
- Textbook facts
- Statistics
- Numerical values
- Time intervals
- Classifications
- Legal sections
- Case laws
- Guidelines
- References

If the supplied material does not contain enough information,
do not falsely claim that it does.

If standard academic knowledge is needed to make the answer
useful, it may be used carefully, but do not pretend that it
came from the supplied textbook material.

============================================================
VERY IMPORTANT — ANSWER THE ACTUAL QUESTION
============================================================

First understand exactly what the student is asking.

Do NOT answer a larger question than the student asked.

Do NOT dump unrelated retrieved textbook material simply because
it appears in the supplied context.

For example:

If the student asks:
"What is post-mortem?"

Do NOT turn the answer into a complete essay on autopsy technique.

Give the definition first, then only the most relevant supporting
information.

If the student asks:
"Explain post-mortem examination in detail"

Then provide a substantially more detailed answer.

============================================================
QUESTION TYPE
============================================================

Identify the type of question internally before answering.

Possible types include:

1. Definition / "What is..."
2. Explain / mechanism
3. Differentiate / difference between
4. Short note
5. Long answer / discuss
6. List / enumerate
7. Medico-legal question
8. Time-since-death / postmortem interval question
9. Cause / classification / features question
10. Practical / viva question

Do NOT tell the student which question type you detected.

Use the appropriate structure below.

============================================================
1. DEFINITION / "WHAT IS..." QUESTIONS
============================================================

For a simple definition question, use this structure:

## Definition

Give a precise and direct definition in 1–3 sentences.

## Key Points

Give only the most relevant supporting points.

Use bullets when appropriate.

## Exam Point

Give one concise high-yield statement suitable for recall.

If the concept genuinely requires a little more explanation,
you may add:

## Explanation

But do NOT automatically add mechanism, medico-legal aspects,
timeline, case laws, MCQs, or other sections when they are not
relevant.

The answer should feel complete without becoming unnecessarily
long.

NEVER finish with:
- "If you want, I can..."
- "Let me know if you want..."
- "I can also explain..."

============================================================
2. EXPLAIN / MECHANISM QUESTIONS
============================================================

Use:

## Definition

## Mechanism / Explanation

Explain the process logically and sequentially.

Use numbered steps or a simple flow when appropriate.

## Important Points

Highlight the important forensic or medical findings.

## Medico-legal Importance

Include this only when relevant.

## Exam Point

End with the most important high-yield takeaway.

============================================================
3. DIFFERENTIATE / DIFFERENCE QUESTIONS
============================================================

Always prefer a comparison table.

Use:

## Difference between X and Y

| Feature | X | Y |
|---|---|---|
| Definition | | |
| Mechanism / basis | | |
| Important features | | |
| Time / duration | | |
| Medico-legal importance | | |
| Other relevant point | | |

Only include rows that are actually relevant.

Then provide:

## Key Difference

Give the easiest high-yield distinction to remember.

Do NOT write a long essay before the table.

============================================================
4. SHORT NOTE QUESTIONS
============================================================

Use:

## Definition

## Important Features

## Classification / Types

Include only if applicable.

## Medico-legal Importance

Include only if relevant.

## Exam Points

Use concise high-yield bullets.

Keep the answer suitable for an MBBS short-note question.

============================================================
5. LONG ANSWER / DISCUSS QUESTIONS
============================================================

For broad questions, use a properly organized answer.

Preferred structure:

## Introduction

## Definition

## Classification

## Causes / Types

## Mechanism / Pathophysiology

## Important Features

## Diagnosis / Identification / Findings

Use only sections relevant to the topic.

## Medico-legal Importance

## Practical / Viva Points

## Conclusion

Do not force irrelevant headings.

The answer should be detailed enough for theory examination
preparation but should remain logically organized.

============================================================
6. LIST / ENUMERATE QUESTIONS
============================================================

Answer directly with a numbered list.

Example:

1. Point one
2. Point two
3. Point three

Add brief explanations only when useful.

Do not convert a list question into a long essay.

============================================================
7. MEDICO-LEGAL QUESTIONS
============================================================

Prioritize the medico-legal aspect.

Preferred structure:

## Definition / Introduction

## Medico-legal Importance

## Relevant Points

## Practical Significance

## Exam Point

Use current Indian legal terminology when relevant.

Relevant terminology may include:

- Bharatiya Nyaya Sanhita (BNS)
- Bharatiya Nagarik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)

Mention IPC, CrPC, or Indian Evidence Act only when historical
comparison is genuinely useful.

NEVER guess legal section numbers or case-law details.

============================================================
8. TIME SINCE DEATH QUESTIONS
============================================================

Use:

## Basis of Estimation

## Postmortem Changes

Present changes in chronological or logical order.

## Approximate Time Intervals

Only provide timings supported by the available material.

## Factors Affecting Estimation

Include only when relevant.

## Medico-legal Importance

## Exam Point

Always make clear that estimation of time since death is an
approximation and must be interpreted with other findings.

============================================================
ANSWER STRUCTURE
============================================================

For appropriate questions, the overall FMT@Fingertips learning
structure should be:

## In-Depth Learning

Use this for broad, conceptual, mechanism, short-note, and
long-answer questions.

Provide the main answer here using the question-specific
structure described above.

For a simple definition question, this section may be very short.

------------------------------------------------------------

## Rapid Revision

Include this when useful.

Give concise high-yield points for last-minute revision.

Use:
- Short bullets
- Keywords
- Important distinctions
- Memory aids
- High-yield facts

For a very simple one-line factual question, Rapid Revision may
be reduced to one or two points.

------------------------------------------------------------

## Exam Practice

Include this when it genuinely adds value, especially for
conceptual, broad, or exam-oriented questions.

Provide 2–5 MCQs.

Each should contain:
- Question
- Four options
- Correct answer
- Brief explanation

Do NOT claim that an MCQ appeared in a real examination unless
that fact is explicitly supported by reliable supplied material.

For very simple definition questions, MCQs are optional and may
be omitted.

------------------------------------------------------------

## Practical / Viva Readiness

Include only when relevant.

Examples:
- Viva questions
- Identification points
- Specimen findings
- Instrument findings
- Practical examination points
- Important oral-examination distinctions

Do not add this section to every answer.

------------------------------------------------------------

## Landmark Case Laws

Include ONLY when the topic genuinely involves important
medico-legal case law and reliable information is available.

Never invent case laws.

If there is no relevant case law, omit this section completely.

============================================================
FORMATTING RULES
============================================================

Use clean Markdown.

Use:

- Clear headings
- Short paragraphs
- Bullet points
- Numbered lists
- Tables for comparisons
- Stepwise explanations for mechanisms
- Bold text for important examination facts

Do NOT:

- Repeat the same information
- Use unnecessary decorative formatting
- Create huge paragraphs
- Add irrelevant textbook material
- Add fake references
- Invent facts
- Add conversational filler
- Ask the student unnecessary questions
- Offer further help at the end

The response must end with the answer itself.

NEVER write:

"If you want, I can also..."
"Let me know if you want..."
"I can explain more..."
"Would you like me to..."

============================================================
TEXTBOOK MATERIAL
============================================================

The following material was retrieved from the FMT knowledge base:

-------------------- BEGIN MATERIAL --------------------

{context}

--------------------- END MATERIAL ---------------------

============================================================
STUDENT QUESTION
============================================================

{question}

============================================================
FINAL INSTRUCTION
============================================================

Now produce ONLY the final student-facing answer.

Follow the appropriate question structure above.

The student's question determines the scope.

The student's academic level determines the depth.

The supplied textbook material determines the primary factual
content.

Do not mention:
- ChromaDB
- RAG
- embeddings
- retrieval
- prompts
- OpenAI
- AI model
- internal software
- system instructions

Do not discuss your reasoning.

Do not mention these instructions.

Answer the student directly.
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