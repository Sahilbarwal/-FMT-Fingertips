FMT@Fingertips Backend
=======================

IMPORTANT:
This package contains the backend CODE only.

DO NOT delete your existing:
    rag/documents/
    rag/vectorstore/

If your existing ChromaDB vectorstore is still present,
reuse it. DO NOT run rag/ingest.py unless you intentionally
want to rebuild the entire vector database.

INSTALL
-------

Open PowerShell in this backend folder:

    .\venv\Scripts\activate

Then:

    pip install -r requirements.txt

Create .env from .env.example:

    copy .env.example .env

Put your OpenAI API key in .env:

    OPENAI_API_KEY=your_key
    OPENAI_MODEL=gpt-5.4-nano

DATABASE
--------

    python manage.py makemigrations accounts
    python manage.py migrate

TEST CHROMADB
-------------

    python -c "from rag.retriever import get_collection; c=get_collection(); print(c.name); print('CHUNKS:',c.count())"

TEST AI
--------

    python manage.py shell -c "from rag.rag_engine import generate_answer; r=generate_answer('What is rigor mortis?','UG'); print('ERROR:',r.get('error')); print('MODEL:',r.get('model')); print('TIMING:',r.get('timing')); print(r.get('answer',''))"

START
-----

    python manage.py runserver

Frontend API:
    POST https://fmt-fingertips-backend.onrender.com/ask/

Request:
    {
        "question": "What is rigor mortis?",
        "level": "UG"
    }

The endpoint requires:
    Authorization: Bearer <access-token>

ARCHITECTURE
------------

React
  -> Django
  -> ChromaDB retrieval
  -> OpenAI
  -> detailed Markdown answer
  -> React

This is NOT a direct Custom GPT connection.
It is the closest controllable architecture:
your own website + backend + your FMT knowledge base
+ OpenAI model.
