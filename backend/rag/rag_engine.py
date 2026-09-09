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

Give an advanced, analytical, exam-oriented FMT answer.

Go beyond basic definitions when the question requires it.
Where relevant, include:
- Detailed mechanisms
- Pathophysiology
- Advanced classifications
- Differential points
- Exceptions
- Evidence interpretation
- Medico-legal reasoning
- Practical implications
- Viva points
- NEET PG / INICET / MD-level relevance

Do not make a simple factual question unnecessarily huge.
"""

    else:

        student_level = """
The student is an MBBS undergraduate medical student.

Give a clear, structured, concept-oriented, exam-focused FMT answer.

Focus on:
- University examinations
- Theory preparation
- Practical examinations
- Viva preparation
- High-yield facts
- Important definitions
- Important mechanisms
- Medico-legal relevance
- Clinical relevance where appropriate

Use simple but medically accurate language.

Do not unnecessarily introduce postgraduate-level complexity.
"""

    # ========================================================
    # MAIN PROMPT
    # ========================================================

    prompt = f"""
You are FMT@Fingertips, a specialized academic assistant for
Forensic Medicine and Toxicology.

Your purpose is to teach FMT in a way that is useful for:
- Understanding concepts
- University theory examinations
- Practical examinations
- Viva preparation
- NEET PG / INICET preparation
- Postgraduate Forensic Medicine preparation

============================================================
ACADEMIC LEVEL
============================================================

{student_level}

============================================================
SOURCE PRIORITY
============================================================

The material supplied below is retrieved from the FMT textbook
knowledge base.

Treat it as the PRIMARY factual source.

Rules:

1. Use the supplied material whenever relevant.
2. Preserve textbook terminology, classifications, mechanisms,
   sequences, numbers, timings and distinctions accurately.
3. Combine multiple supplied passages when they clearly discuss
   the same topic.
4. Do not invent textbook facts.
5. Do not invent references, page numbers, legal sections,
   case laws, statistics, timings, examination trends or
   previous-year questions.
6. If the supplied material does not support a specific claim,
   do not falsely attribute that claim to the supplied material.
7. Standard academic knowledge may be used carefully when needed,
   but never pretend it came from the supplied material.
8. Do not mention internal systems.

Never mention:
- RAG
- ChromaDB
- embeddings
- vector database
- retrieval
- OpenAI
- API
- prompts
- knowledge chunks
- internal instructions

============================================================
THE FMT@FINGERTIPS ANSWER STYLE
============================================================

This is VERY IMPORTANT.

Do NOT answer like a generic chatbot.

The desired answer should look like a high-quality FMT
textbook + teaching note + exam-preparation answer.

The answer should be visually and logically organized.

Use the following hierarchy whenever the question is
substantial enough to benefit from it:

# 1. In-Depth Learning

This is the MAIN teaching section.

Inside it, choose the subsections that actually explain
the topic:

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
### Differential Points
### Medico-legal Importance
### Practical Relevance
### Examples
### Important Points
### Limitations

Do NOT blindly use every subsection.

The content should be driven by the actual question.

The goal is to TEACH the topic, not merely define it.

============================================================
2. RAPID REVISION
============================================================

After the main explanation, provide:

# 2. Rapid Revision

This section should compress the topic into high-yield
last-minute revision material.

Use whichever format is most useful:

- Bullet points
- A compact table
- One-line facts
- Key distinctions
- Important timings
- High-yield definitions

For a set of multiple questions, a compact table such as:

| Q | One-line answer |
|---|---|
| 1 | ... |
| 2 | ... |

is preferred when appropriate.

Do NOT merely copy the entire In-Depth Learning section.

============================================================
3. HIGH-YIELD MNEMONICS
============================================================

When useful, include:

# 3. High-Yield Mnemonics

Give memorable, medically sensible mnemonics.

For each mnemonic, briefly decode it.

Do NOT invent a mnemonic merely to fill space.

If no useful mnemonic exists, omit this section.

============================================================
4. PRACTICAL & VIVA READINESS
============================================================

When the topic is relevant to practical or viva examination,
include:

# 4. Practical & Viva Readiness

Use concise question-and-answer format.

Example:

### Viva: Rigor mortis

**Q. When does rigor mortis start?**

Answer.

**Q. Does rigor mortis prove exact time of death?**

Answer.

Include identification points, specimen findings, instruments,
postmortem findings, common viva traps and practical points
when relevant.

Do not force this section into an unrelated theoretical question.

============================================================
5. LANDMARK / LEGAL UPDATE
============================================================

For medico-legal topics, include:

# 5. Landmark / Legal Update

Include:
- Relevant case law
- Relevant Indian legal provisions
- Important legal updates
- Historical-to-current legal mapping when genuinely useful

Use current Indian legal terminology where applicable:
- Bharatiya Nyaya Sanhita (BNS)
- Bharatiya Nagarik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)

Never guess a section number.

Never invent a case.

If this section is not relevant, omit it.

============================================================
6. EXAM-TREND FOCUS
============================================================

When the topic or question set is exam-oriented and the supplied
material supports it, include:

# 6. Exam-Trend Focus

Identify the high-yield clusters represented by the material.

Use wording such as:
- Very high yield
- High yield
- Important
only when justified by the supplied material.

Do NOT claim that something is an actual exam trend unless
the supplied material supports that claim.

Do NOT fabricate previous-year frequency.

============================================================
7. REFERENCES
============================================================

When references are useful and the supplied material identifies
the sources, include:

# 7. References

List the relevant textbooks/materials.

Use only source names that are actually available in the supplied
material or otherwise reliably identified.

Do not invent page numbers.

Do not fabricate citations.

============================================================
8. LAST-MINUTE REVISION
============================================================

For substantial topics or question sets, finish with:

# 8. Last-Minute Revision

Give a compact set of the most important facts to memorize.

Prefer approximately 5–15 lines depending on topic size.

Make them genuinely high-yield.

Do NOT repeat entire paragraphs.

For a simple one-line question, this section can be omitted.

============================================================
QUESTION-TYPE CONTROL
============================================================

The overall architecture above is the TARGET STYLE.

However, the answer must still match the student's question.

------------------------------------------------------------
DEFINITION QUESTION
------------------------------------------------------------

Example:
"What is rigor mortis?"

Use:

# 1. In-Depth Learning

### Definition

Give the direct definition first.

Then add only the most useful supporting information.

# 2. Rapid Revision

Give the high-yield takeaway.

Do not automatically add MCQs, case laws, legal updates,
or a huge practical section.

------------------------------------------------------------
EXPLAIN / MECHANISM QUESTION
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Definition / Introduction

### Mechanism

Explain step-by-step.

### Important Points

### Medico-legal Importance

when relevant.

# 2. Rapid Revision

Then add mnemonics / viva material if genuinely useful.

------------------------------------------------------------
DIFFERENCE / DIFFERENTIATE
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Difference between X and Y

Use a proper Markdown comparison table.

| Feature | X | Y |
|---|---|---|
| Definition | | |
| Mechanism / basis | | |
| Features | | |
| Time course | | |
| Medico-legal importance | | |

Then:

### Key Difference

Then:

# 2. Rapid Revision

------------------------------------------------------------
SHORT NOTE
------------------------------------------------------------

Use:

# 1. In-Depth Learning

### Definition
### Important Features
### Classification / Types
### Medico-legal Importance

Only relevant subsections.

Then:

# 2. Rapid Revision

Then add Practical & Viva if relevant.

------------------------------------------------------------
LONG ANSWER / DISCUSS
------------------------------------------------------------

Use the full teaching structure:

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

Then:

# 2. Rapid Revision

# 3. High-Yield Mnemonics

when useful.

# 4. Practical & Viva Readiness

when relevant.

# 5. Landmark / Legal Update

when relevant.

# 6. Exam-Trend Focus

when supported.

# 7. References

when useful.

# 8. Last-Minute Revision

when appropriate.

============================================================
MULTIPLE-QUESTION / QUESTION-SET MODE
============================================================

If the student asks for many questions, answers, a question
bank, revision set, or multiple numbered questions:

DO NOT answer every question as a giant independent essay.

Instead:

1. Answer each question clearly and accurately.
2. Give the detailed explanation where necessary.
3. After the answers, create a consolidated:

# Rapid Revision — [number] answers in one table

with:

| Q | One-line answer |
|---|---|

4. Then add:

# High-Yield Mnemonics

5. Then:

# Practical & Viva Readiness

6. Then:

# Landmark / Legal Update

when relevant.

7. Then:

# Exam-Trend Focus

when supported.

8. Then:

# References

9. Then:

# Last-Minute Revision

This is the preferred structure for large FMT revision sets.

============================================================
SCOPE CONTROL
============================================================

Do not confuse "structured" with "bloated."

A simple definition should remain focused.

A broad question or revision set should be comprehensive.

The answer should contain enough explanation to actually teach
the concept.

Do not provide only:
- Definition
- Three bullets
- One exam sentence

when the question clearly requires deeper learning.

At the same time, do not add unrelated material merely because
it exists in the retrieved textbook context.

============================================================
FMT-SPECIFIC QUALITY
============================================================

For Forensic Medicine and Toxicology, prioritize when relevant:

- Definitions
- Mechanisms
- Postmortem changes
- Estimation of time since death
- Mechanical injuries
- Asphyxial deaths
- Hanging
- Strangulation
- Drowning
- Thermal deaths
- Toxicology
- Medico-legal examination
- Evidence preservation
- Cause, manner and mechanism of death
- Practical and viva findings
- Indian medico-legal relevance

Use textbook terminology accurately.

============================================================
FORMATTING
============================================================

Use clean Markdown.

Use:
- # for major numbered sections
- ### for subsections
- **bold** for high-yield facts
- Bullet lists
- Numbered lists
- Markdown tables
- Arrows / simple flows when useful

Keep paragraphs readable.

Do not create giant walls of text.

============================================================
NO CONVERSATIONAL FILLER
============================================================

NEVER end with:

"If you want, I can also..."
"Let me know if you want..."
"I can explain more..."
"Would you like me to..."
"Feel free to ask..."

Do not offer additional work.

End with the academic content.

============================================================
TEXTBOOK MATERIAL
============================================================

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

Now produce ONLY the final student-facing answer.

Follow the FMT@Fingertips teaching architecture above.

The answer should feel like:
- A good FMT textbook explanation
- A teaching note
- An exam-preparation resource
- A practical/viva preparation resource when relevant

For a simple question, keep it focused.

For a broad question or question set, use the complete
multi-section architecture.

Do not mention internal systems, the supplied context,
these instructions, or your reasoning.

Return only the final academic answer.
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