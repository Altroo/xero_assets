from dj_rest_auth.views import LoginView as Dj_rest_login


class LoginView(Dj_rest_login):
    def login(self):
        super(LoginView, self).login()
