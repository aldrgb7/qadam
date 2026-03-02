from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Разрешает аутентификацию по username ИЛИ по email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Ищем пользователя, у которого username=введенному ИЛИ email=введенному
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Если вдруг (хотя не должно) нашлось два юзера с одинаковой почтой
            user = UserModel.objects.filter(email__iexact=username).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None