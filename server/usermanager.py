class UserManager:
    """Classe que gerencia a lista (dicionario) de usuarios"""
    def __init__(self):
        self.userdict = {}
        
    def user_login(self, username, user_obj):
        if username in self.userdict:
            raise RuntimeError("The user was already logged in!")
        self.userdict[username] = user_obj

    def user_logoff(self, username):
        if username not in self.userdict:
            raise RuntimeError("The user was not logged in!")
        del self.userdict[username]

    def get_list(self):
        return self.userdict