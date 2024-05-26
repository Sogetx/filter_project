from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Забороняємо логінізацію, якщо пошта не підтверджена
        return request.user.is_authenticated or self.get_login_redirect_url(request) == self.get_signup_redirect_url(request)