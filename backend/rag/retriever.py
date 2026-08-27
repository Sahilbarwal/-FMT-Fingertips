import chromadb

from pathlib import Path
from collections import defaultdict


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

VECTORSTORE_DIR = BASE_DIR / "vectorstore"


# ============================================================
# SETTINGS
# ============================================================

COLLECTION_NAME = "fmt_knowledge_base"

# Number of chunks finally sent to the AI
TOP_K = 10

# ChromaDB searches the entire knowledge base and returns
# the top 100 most relevant candidates
INITIAL_RESULTS = 100

# Maximum number of chunks allowed from one PDF
MAX_CHUNKS_PER_SOURCE = 3


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=str(VECTORSTORE_DIR)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# NORMALIZE SOURCE NAME
# ============================================================

def normalize_source(source):

    if not source:
        return "Unknown source"

    return str(source).strip()


# ============================================================
# CONVERT CHUNK NUMBER
# ============================================================

def get_chunk_number(chunk):

    try:
        return int(chunk)

    except (TypeError, ValueError):
        return None


# ============================================================
# CHECK IF CHUNK IS NEAR AN ALREADY SELECTED CHUNK
# ============================================================

def is_nearby_chunk(candidate, selected):

    candidate_source = candidate["source"]

    candidate_chunk = get_chunk_number(
        candidate["chunk"]
    )

    if candidate_chunk is None:
        return False


    for selected_item in selected:

        if (
            selected_item["source"]
            != candidate_source
        ):
            continue


        selected_chunk = get_chunk_number(
            selected_item["chunk"]
        )

        if selected_chunk is None:
            continue


        # Avoid immediately consecutive chunks
        if abs(
            candidate_chunk - selected_chunk
        ) <= 1:

            return True


    return False


# ============================================================
# RETRIEVE CONTEXT
# ============================================================

def retrieve_context(question, top_k=TOP_K):


    # --------------------------------------------------------
    # VALIDATE QUESTION
    # --------------------------------------------------------

    if not question or not question.strip():

        print("WARNING: Empty question.")

        return []


    # --------------------------------------------------------
    # CHECK KNOWLEDGE BASE
    # --------------------------------------------------------

    try:

        total_documents = collection.count()

    except Exception as error:

        print(
            "ChromaDB count error:",
            error
        )

        return []


    if total_documents == 0:

        print(
            "WARNING: Knowledge base is empty."
        )

        return []


    # --------------------------------------------------------
    # NUMBER OF CANDIDATES TO RETRIEVE
    # --------------------------------------------------------

    initial_results = max(
        INITIAL_RESULTS,
        top_k * 10
    )

    initial_results = min(
        initial_results,
        total_documents
    )


    # ========================================================
    # DEBUG
    # ========================================================

    print("\n")
    print("=" * 70)
    print("RAG RETRIEVAL DEBUG")
    print("=" * 70)

    print(
        "Question:",
        question
    )

    print(
        "Total chunks in knowledge base:",
        total_documents
    )

    print(
        "Candidates requested:",
        initial_results
    )

    print("=" * 70)


    # ========================================================
    # QUERY CHROMADB
    #
    # This searches the entire vector collection.
    # ========================================================

    try:

        results = collection.query(

            query_texts=[
                question
            ],

            n_results=initial_results,

            include=[
                "documents",
                "metadatas",
                "distances"
            ]

        )

    except Exception as error:

        print(
            "ChromaDB retrieval error:",
            error
        )

        return []


    # ========================================================
    # EXTRACT RESULTS
    # ========================================================

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]


    candidates = []


    # ========================================================
    # BUILD CANDIDATE LIST
    # ========================================================

    for index, document in enumerate(documents):


        if not document:
            continue


        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        metadata = {}

        if index < len(metadatas):

            metadata = (
                metadatas[index]
                or {}
            )


        # ----------------------------------------------------
        # DISTANCE
        # ----------------------------------------------------

        distance = None

        if index < len(distances):

            distance = distances[index]


        # ----------------------------------------------------
        # SOURCE NAME
        # ----------------------------------------------------

        source = normalize_source(

            metadata.get(
                "source",
                "Unknown source"
            )

        )


        # ----------------------------------------------------
        # CHUNK NUMBER
        # ----------------------------------------------------

        chunk = metadata.get(
            "chunk",
            "Unknown"
        )


        candidates.append(

            {
                "text": document,

                "source": source,

                "chunk": chunk,

                "distance": distance
            }

        )


    # ========================================================
    # SORT BY RELEVANCE
    #
    # Lower distance = better match
    # ========================================================

    candidates.sort(

        key=lambda item:

            float("inf")

            if item["distance"] is None

            else float(item["distance"])

    )


    # ========================================================
    # SHOW TOP 30 RAW RESULTS
    # ========================================================

    print("\n")
    print("TOP 30 RAW RESULTS")
    print("-" * 70)


    for index, item in enumerate(
        candidates[:30],
        start=1
    ):

        print(

            f"{index}. "

            f"Source: {item['source']} | "

            f"Chunk: {item['chunk']} | "

            f"Distance: {item['distance']}"

        )


    print("-" * 70)


    # ========================================================
    # GROUP CANDIDATES BY SOURCE
    #
    # Example:
    #
    # sources = {
    #   "Reddy.pdf": [...],
    #   "Modi.pdf": [...],
    #   "AIIMS syllabus.pdf": [...]
    # }
    # ========================================================

    sources = defaultdict(list)


    for item in candidates:

        sources[
            item["source"]
        ].append(
            item
        )


    # ========================================================
    # SORT CHUNKS INSIDE EACH SOURCE
    # ========================================================

    for source in sources:

        sources[source].sort(

            key=lambda item:

                float("inf")

                if item["distance"] is None

                else float(item["distance"])

        )


    # ========================================================
    # SORT SOURCES
    #
    # A source whose best chunk has the best distance
    # appears first.
    # ========================================================

    sorted_sources = sorted(

        sources.keys(),

        key=lambda source:

            float("inf")

            if not sources[source]

            else (

                float("inf")

                if sources[source][0]["distance"] is None

                else float(
                    sources[source][0]["distance"]
                )

            )

    )


    # ========================================================
    # FINAL SELECTION
    # ========================================================

    selected = []

    source_counts = defaultdict(int)


    # ========================================================
    # PASS 1
    #
    # Take ONE BEST chunk from each relevant PDF first.
    #
    # This creates diversity.
    # ========================================================

    for source in sorted_sources:


        if len(selected) >= top_k:
            break


        source_items = sources[source]


        if not source_items:
            continue


        item = source_items[0]


        selected.append(
            item
        )


        source_counts[source] += 1


    # ========================================================
    # PASS 2
    #
    # Add second/third chunks from relevant PDFs.
    # ========================================================

    round_number = 1


    while len(selected) < top_k:


        added_something = False


        for source in sorted_sources:


            if len(selected) >= top_k:
                break


            # Maximum 3 chunks per source
            if (
                source_counts[source]
                >= MAX_CHUNKS_PER_SOURCE
            ):
                continue


            source_items = sources[source]


            # No more chunks from this source
            if (
                round_number
                >= len(source_items)
            ):
                continue


            item = source_items[
                round_number
            ]


            # ------------------------------------------------
            # CHECK DUPLICATE
            # ------------------------------------------------

            duplicate = any(

                (
                    selected_item["source"]
                    == item["source"]

                    and

                    str(
                        selected_item["chunk"]
                    )
                    == str(
                        item["chunk"]
                    )

                )

                for selected_item
                in selected

            )


            if duplicate:
                continue


            # ------------------------------------------------
            # AVOID NEARBY CHUNKS
            # ------------------------------------------------

            if is_nearby_chunk(
                item,
                selected
            ):
                continue


            # ------------------------------------------------
            # ADD CHUNK
            # ------------------------------------------------

            selected.append(
                item
            )


            source_counts[source] += 1


            added_something = True


        # ----------------------------------------------------
        # STOP IF NOTHING NEW WAS ADDED
        # ----------------------------------------------------

        if not added_something:
            break


        round_number += 1


    # ========================================================
    # FINAL DEBUG
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL SELECTED CONTEXT")
    print("=" * 70)


    for index, item in enumerate(
        selected,
        start=1
    ):

        print(

            f"{index}. "

            f"Source: {item['source']} | "

            f"Chunk: {item['chunk']} | "

            f"Distance: {item['distance']}"

        )


    print("\n")
    print("SOURCE DISTRIBUTION")
    print("-" * 70)


    for source, count in source_counts.items():

        print(

            f"{source}: "

            f"{count} chunk(s)"

        )


    print("=" * 70)
    print("\n")


    # ========================================================
    # CLEAN FINAL RESULTS
    # ========================================================

    final_results = []


    for item in selected:


        final_results.append(

            {
                "text": item["text"],

                "source": item["source"],

                "chunk": item["chunk"],

                "distance": item["distance"]
            }

        )


    return final_results


# ============================================================
# BUILD CONTEXT FOR GPT
# ============================================================

def build_context(results):


    context_parts = []


    for index, item in enumerate(
        results,
        start=1
    ):


        context_parts.append(

            f"""
============================================================
SOURCE {index}
============================================================

PDF / BOOK:
{item["source"]}

CHUNK:
{item["chunk"]}

CONTENT:
{item["text"]}
"""

        )


    return "\n".join(
        context_parts
    )