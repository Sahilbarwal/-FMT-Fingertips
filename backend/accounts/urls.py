from django.urls import path
from . import views


urlpatterns = [

    # Authentication
    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login,
        name="login"
    ),

    path(
        "logout/",
        views.logout,
        name="logout"
    ),


    # User / Profile
    path(
        "me/",
        views.me,
        name="me"
    ),

    path(
        "profile/",
        views.me,
        name="profile"
    ),


    # Search History
    path(
        "history/",
        views.history,
        name="history"
    ),


    # FMT AI Assistant
    path(
        "ask/",
        views.ask,
        name="ask"
    ),

    # FMT AI Assistant - Streaming
    path(
        "ask/stream/",
        views.ask_stream,
        name="ask_stream"
    ),
]