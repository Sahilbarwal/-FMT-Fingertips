from django.contrib.auth import authenticate
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

from rag.rag_engine import generate_answer


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
                "error": "Email and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Find user using their email
    from django.contrib.auth.models import User

    try:
        user_object = User.objects.get(
            email__iexact=email
        )

    except User.DoesNotExist:
        return Response(
            {
                "error": "Invalid email or password."
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Authenticate with actual username
    user = authenticate(
        username=user_object.username,
        password=password,
    )

    if user is None:
        return Response(
            {
                "error": "Invalid email or password."
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
# FMT AI ASSISTANT
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask(request):
    """
    Main FMT Assistant endpoint.

    Frontend sends:

    {
        "question": "What is rigor mortis?",
        "level": "UG"
    }

    Flow:

    React
       ↓
    Django
       ↓
    ChromaDB retrieval
       ↓
    Relevant FMT textbook chunks
       ↓
    OpenAI
       ↓
    Detailed answer
       ↓
    React
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
    # SAVE TO HISTORY
    # --------------------------------------------------------

    try:

        SearchHistory.objects.create(
            user=request.user,
            question=question,
            answer=answer,
        )

    except Exception as error:

        # History failure should NOT prevent
        # the student from receiving the answer.

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