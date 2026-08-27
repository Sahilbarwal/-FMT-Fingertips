from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):

    # Frontend sends full_name instead of username
    full_name = serializers.CharField(
        write_only=True,
        required=True
    )

    password = serializers.CharField(
        write_only=True,
        min_length=6
    )


    class Meta:

        model = User

        fields = [
            "full_name",
            "email",
            "password",
        ]

        extra_kwargs = {

            "email": {
                "required": True,
            },

        }


    # ============================================================
    # VALIDATE EMAIL
    # ============================================================

    def validate_email(self, value):

        email = value.strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():

            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return email


    # ============================================================
    # CREATE USER
    # ============================================================

    def create(self, validated_data):

        # Get full name
        full_name = validated_data.pop(
            "full_name"
        ).strip()


        # Get email
        email = validated_data.get(
            "email"
        ).strip().lower()


        # Get password
        password = validated_data.pop(
            "password"
        )


        # ========================================================
        # SPLIT FULL NAME
        # ========================================================

        name_parts = full_name.split(
            " ",
            1
        )


        first_name = name_parts[0]


        last_name = ""

        if len(name_parts) > 1:

            last_name = name_parts[1]


        # ========================================================
        # CREATE USER
        #
        # IMPORTANT:
        # Email is automatically used as username.
        # The user does NOT need to enter a username.
        # ========================================================

        user = User.objects.create_user(

            username=email,

            email=email,

            password=password,

            first_name=first_name,

            last_name=last_name,

        )


        return user