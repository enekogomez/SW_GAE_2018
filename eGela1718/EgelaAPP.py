import logging as lg

'''
session = rqs.session()
#session.cookies.items()
r = session.post('https://google.com')

for kv in r.headers.items():
    print(kv[0] + '\t' + kv[1])
print(r.url)
'''

from eGela1718 import SubMenu
from eGela1718 import User

lg.basicConfig(format='%(asctime)s : %(levelname)s: %(message)s', level=lg.INFO)


class EgelaAPP:

    def __init__(self, login_host='https://egela1718.ehu.eus/login/index.php'):
        self.LOGIN_HOST = login_host
        self.logged = False

    def create_user(self):
        #Se crea un nuevo usuario y se inicia una request.session
        username = input('Introduzca el identificador de usuario LDAP:\t')
        self.user = User.User(username)
        password = input('Introduce la contraseña de usuario:\t')
        self.user.set_pass(password)

    def logout(self):
        try:
            self.user.getSession().close()
            self.user = None
            self.menu()
        except AttributeError as e:
            print("No user registered.")
            self.menu()

    def login(self):
        credentials = {
            'username': self.user.get_username(),
            'password': self.user.get_pass()
        }
        lg.info('Sending post to ' + self.LOGIN_HOST)
        post = self.user.getSession().post(self.LOGIN_HOST, data=credentials)
        lg.info('DONE')
        cookies = self.user.getSession().cookies
        print("\n\t===============COOKIE ====================")
        for kv in cookies.items():
            print('\t' + kv[0] + ':\t' + kv[1])
        print("\t=========================================")
        # response = self.user.getSession().get('https://egela1718.ehu.eus/')
        if post.headers["Expires"] is not '':
            self.logged = True

        self.print_headers(post)
        # print(response)




    @staticmethod
    def print_headers(response):
        print("\t =============RESPONSE HEADERS=============")
        for kv in response.headers.items():
            print('\t' + kv[0] + ':\t' + kv[1])
        print("\t=========================================")

    def GET_url(self,url):
        self.user.getSession().get(url)

    def menu(self):

        print('\n\t\t-----MENÚ PRINCIPAL-----')
        print('\n\t\tSeleccione una opción:')


        print('\t\t1 - Iniciar sesión en eGela')
        print('\t\t2 - Cerrar sesión.')
        print('\t\t3 - Salir de la aplicación')
        option = input('')
        self.process_option(option)
        if self.logged is True:
            self.init_sub_menu()
        self.menu()

    def process_option(self, option=0):
        if option is '1':
            self.logged = False
            self.login_to_eGela()
        elif option is '2':
            self.logged = False
            self.logout()
        elif option is '3':
            exit(0)
        else:
            print('\t------> La opción seleccionada no es válida o no está implementada en la versión actual de la aplicación')
            self.menu()

    def login_to_eGela(self):
        print('Logging in to eGela...')
        self.create_user()
        self.login()
        if self.logged is True:
            print("\n\n ------> Succesfully logged in as: " + self.user.get_username())
        else:
            self.user = None
            print("\n\n ------> Couldn't log in, check your username or password.")

    def execute_app(self):
        print('Bienvenido a la aplicación Python-eGela')
        self.menu()

    def init_sub_menu(self):
        lg.info("Loading application submenu...")
        self.sub_menu = SubMenu.SubMenu(self.user)
        self.sub_menu.load()
        # Se destruye la instancia de sub_menu
        self.sub_menu = None
        self.menu()

    def init_subject_menu(self):
        pass


if __name__ == '__main__':
    app = EgelaAPP()
    app.execute_app()


