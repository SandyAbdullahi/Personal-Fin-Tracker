from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class FlexibleTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Add optional alternates so DRF won't drop them during parsing.
    username = serializers.CharField(required=False, allow_blank=True)
    identifier = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user_field = self.username_field  # e.g. "email" if your CustomUser uses email
        supplied = attrs.get(user_field) or attrs.get("username") or attrs.get("identifier")
        if not supplied:
            raise serializers.ValidationError({user_field: f"{user_field} is required."})

        # Normalize to the exact field SimpleJWT expects.
        attrs[user_field] = supplied
        attrs.pop("username", None)
        attrs.pop("identifier", None)

        return super().validate(attrs)
