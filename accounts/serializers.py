
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class JetonAvecRoleSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role"] = user.role
        return token

    def validate(self, attrs):
        donnees = super().validate(attrs)
        donnees["username"] = self.user.username
        donnees["role"] = self.user.role
        return donnees
