import json

from django.contrib.auth import authenticate
from django.http import StreamingHttpResponse

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SearchHistory
from .serializers import RegisterSerializer

from rag.rag_engine import (
    generate_answer,
    stream_answer,
)


# ============================================================
# TOKEN HELPER
# ============================================================

def token_response(user):
    """
    Generate JWT access and refresh tokens
    for the authenticated user.
    """

    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }


# ============================================================
# REGISTER
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    """

    serializer = RegisterSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()

    return Response(
        {
            "message": "Registration successful.",
            **token_response(user),
        },
        status=status.HTTP_201_CREATED,
    )


# ============================================================
# LOGIN
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Login using email and password.
    """

    email = request.data.get(
        "email",
        ""
    ).strip().lower()

    password = request.data.get(
        "password",
        ""
    )

    if not email or not password:
        return Response(
            {
                "error":
                "Email and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # FIND USER USING EMAIL
    # --------------------------------------------------------

    from django.contrib.auth.models import User

    try:

        user_object = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:

        return Response(
            {
                "error":
                "Invalid email or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # --------------------------------------------------------
    # AUTHENTICATE USER
    # --------------------------------------------------------

    user = authenticate(
        username=user_object.username,
        password=password,
    )

    if user is None:

        return Response(
            {
                "error":
                "Invalid email or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response(
        {
            "message": "Login successful.",
            **token_response(user),
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# LOGOUT
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint.

    JWT access tokens are normally handled on the
    frontend by deleting the stored token.
    """

    return Response(
        {
            "message":
            "Logout successful."
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# CURRENT USER / PROFILE
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Return information about the currently
    authenticated user.
    """

    user = request.user

    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined,
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# SEARCH HISTORY
# ============================================================

@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def history(request):
    """
    GET    -> return user's history
    POST   -> save a question/answer
    DELETE -> clear user's history
    """

    # --------------------------------------------------------
    # GET HISTORY
    # --------------------------------------------------------

    if request.method == "GET":

        records = SearchHistory.objects.filter(
            user=request.user
        )

        data = []

        for item in records:

            data.append(
                {
                    "id": item.id,
                    "question": item.question,
                    "answer": item.answer,
                    "created_at": item.created_at,
                }
            )

        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    if request.method == "POST":

        question = str(
            request.data.get(
                "question",
                ""
            )
        ).strip()

        answer = str(
            request.data.get(
                "answer",
                ""
            )
        )

        if not question or not answer:

            return Response(
                {
                    "error":
                    "Question and answer are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        record = SearchHistory.objects.create(
            user=request.user,
            question=question,
            answer=answer,
        )

        return Response(
            {
                "message":
                "History saved successfully.",

                "id":
                record.id,

                "question":
                record.question,

                "answer":
                record.answer,
            },
            status=status.HTTP_201_CREATED,
        )

    # --------------------------------------------------------
    # DELETE HISTORY
    # --------------------------------------------------------

    if request.method == "DELETE":

        SearchHistory.objects.filter(
            user=request.user
        ).delete()

        return Response(
            {
                "message":
                "History cleared successfully."
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# FMT AI ASSISTANT — NORMAL ENDPOINT
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask(request):
    """
    Normal non-streaming FMT Assistant endpoint.

    This endpoint is kept for compatibility.

    Frontend sends:

    {
        "question": "What is rigor mortis?",
        "level": "UG"
    }
    """

    # --------------------------------------------------------
    # GET QUESTION
    # --------------------------------------------------------

    question = str(
        request.data.get(
            "question",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # GET LEVEL
    # --------------------------------------------------------

    level = str(
        request.data.get(
            "level",
            "UG"
        )
    ).upper()

    # --------------------------------------------------------
    # VALIDATE QUESTION
    # --------------------------------------------------------

    if not question:

        return Response(
            {
                "error":
                "Question is required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # VALIDATE LEVEL
    # --------------------------------------------------------

    if level not in ["UG", "PG"]:
        level = "UG"

    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    try:

        result = generate_answer(
            question,
            level,
        )

    except Exception as error:

        print(
            "\n========== ASK ERROR =========="
        )

        print(error)

        print(
            "==============================\n"
        )

        return Response(
            {
                "error":
                f"Failed to generate answer: {error}"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # --------------------------------------------------------
    # CHECK RAG / OPENAI ERROR
    # --------------------------------------------------------

    if result.get("error"):

        print(
            "\n========== AI ERROR =========="
        )

        print(
            result.get("error")
        )

        print(
            "==============================\n"
        )

        return Response(
            {
                "error":
                result.get("error"),

                "answer":
                result.get(
                    "answer",
                    ""
                ),

                "sources":
                result.get(
                    "sources",
                    []
                ),

                "timing":
                result.get(
                    "timing"
                ),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # --------------------------------------------------------
    # GET ANSWER
    # --------------------------------------------------------

    answer = str(
        result.get(
            "answer",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # CHECK EMPTY ANSWER
    # --------------------------------------------------------

    if not answer:

        return Response(
            {
                "error":
                "The AI returned an empty answer."
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    try:

        SearchHistory.objects.create(
            user=request.user,
            question=question,
            answer=answer,
        )

    except Exception as error:

        print(
            "History save error:",
            error
        )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return Response(
        {
            "question":
            question,

            "level":
            level,

            "answer":
            answer,

            "sources":
            result.get(
                "sources",
                []
            ),

            "model":
            result.get(
                "model"
            ),

            "source":
            "local_rag_openai",

            "timing":
            result.get(
                "timing"
            ),
        },
        status=status.HTTP_200_OK,
    )


# ============================================================
# FMT AI ASSISTANT — STREAMING ENDPOINT
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask_stream(request):
    """
    Streaming FMT Assistant endpoint.

    Frontend sends:

    {
        "question": "What is rigor mortis?",
        "level": "UG"
    }

    The endpoint returns newline-delimited JSON (NDJSON).

    Example:

    {"type":"meta", ...}
    {"type":"delta","text":"Rigor"}
    {"type":"delta","text":" mortis"}
    {"type":"delta","text":" is"}
    ...
    {"type":"done", ...}
    """

    # --------------------------------------------------------
    # GET QUESTION
    # --------------------------------------------------------

    question = str(
        request.data.get(
            "question",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # GET LEVEL
    # --------------------------------------------------------

    level = str(
        request.data.get(
            "level",
            "UG"
        )
    ).upper().strip()

    # --------------------------------------------------------
    # VALIDATE QUESTION
    # --------------------------------------------------------

    if not question:

        return Response(
            {
                "error":
                "Question is required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # VALIDATE LEVEL
    # --------------------------------------------------------

    if level not in ["UG", "PG"]:
        level = "UG"

    # --------------------------------------------------------
    # STREAM GENERATOR
    # --------------------------------------------------------

    def event_stream():

        final_answer = ""

        final_sources = []

        final_model = None

        final_timing = None

        try:

            # ------------------------------------------------
            # GET EVENTS FROM RAG ENGINE
            # ------------------------------------------------

            for event in stream_answer(
                question,
                level
            ):

                event_type = event.get(
                    "type"
                )

                # --------------------------------------------
                # METADATA
                # --------------------------------------------

                if event_type == "meta":

                    final_sources = event.get(
                        "sources",
                        []
                    )

                    final_model = event.get(
                        "model"
                    )

                # --------------------------------------------
                # TEXT DELTA
                # --------------------------------------------

                elif event_type == "delta":

                    final_answer += event.get(
                        "text",
                        ""
                    )

                # --------------------------------------------
                # FINAL EVENT
                # --------------------------------------------

                elif event_type == "done":

                    final_answer = event.get(
                        "answer",
                        final_answer
                    )

                    final_sources = event.get(
                        "sources",
                        final_sources
                    )

                    final_model = event.get(
                        "model",
                        final_model
                    )

                    final_timing = event.get(
                        "timing"
                    )

                # --------------------------------------------
                # SEND EVENT TO FRONTEND
                # --------------------------------------------

                yield (
                    json.dumps(
                        event,
                        ensure_ascii=False
                    )
                    + "\n"
                )

            # ------------------------------------------------
            # SAVE COMPLETED ANSWER TO HISTORY
            # ------------------------------------------------

            if final_answer.strip():

                try:

                    SearchHistory.objects.create(
                        user=request.user,
                        question=question,
                        answer=final_answer.strip(),
                    )

                except Exception as error:

                    print(
                        "Streaming history save error:",
                        error
                    )

        except Exception as error:

            print()
            print(
                "========== STREAM ERROR =========="
            )

            print(error)

            print(
                "================================="
            )

            print()

            error_event = {
                "type": "error",
                "error":
                f"Failed to generate answer: {error}"
            }

            yield (
                json.dumps(
                    error_event,
                    ensure_ascii=False
                )
                + "\n"
            )

    # --------------------------------------------------------
    # STREAMING HTTP RESPONSE
    # --------------------------------------------------------

    response = StreamingHttpResponse(
        event_stream(),
        content_type=(
            "application/x-ndjson; "
            "charset=utf-8"
        ),
    )

    # --------------------------------------------------------
    # PREVENT CACHING
    # --------------------------------------------------------

    response["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    # --------------------------------------------------------
    # TELL NGINX / PROXY NOT TO BUFFER
    # --------------------------------------------------------

    response["X-Accel-Buffering"] = "no"

    return response