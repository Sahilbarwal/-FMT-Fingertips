from django.contrib import admin
from django.urls import path

from accounts import views


urlpatterns = [

    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin/",
        admin.site.urls
    ),


    # ========================================================
    # AUTHENTICATION
    # ========================================================

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


    # ========================================================
    # USER / PROFILE
    # ========================================================

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


    # ========================================================
    # SEARCH HISTORY
    # ========================================================

    path(
        "history/",
        views.history,
        name="history"
    ),


    # ========================================================
    # FMT AI ASSISTANT
    # ========================================================

    path(
        "ask/",
        views.ask,
        name="ask"
    ),
]