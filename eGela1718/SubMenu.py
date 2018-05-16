import logging as lg
import re
import pymysql
from bs4 import BeautifulSoup as BS
lg.basicConfig(format='%(asctime)s : %(levelname)s: %(message)s', level=lg.INFO)


class SubMenu:



    def __init__(self, user):
        self.HOST = 'https://egela1718.ehu.eus'
        self.user = user

    def load(self):
        print('\n\n\t\t-----eGela 2017/2018-----')
        print('\n\t\tSeleccione una opción:')
        print('\t\t1 - Mostrar lista de asignaturas.')
        print('\t\t2 - Volver al menú principal')
        option = input('')
        self.process_option(option)

    def process_option(self, option='0'):
        if option is '1':
            # Se genera la lista de asignaturas y se añade el diccionario con
            # dicha información al atributo subjects del objeto de la clase User
            if self.user.get_subject_list() is None:
                self.generate_subject_list()
            try:
                # Carga del menú de gestión de asignaturas.
                self.load_subjects_menu()
            except Exception as e:
                print("ERROR: No se ha podido acceder al menú de asignaturas.")
            self.load()
        elif option is '2':
            pass
        else:
            print('\t------> La opción seleccionada no es válida o no está implementada en la versión actual de la aplicación')
            self.load()

    def generate_subject_list(self):
        lg.info('Loading info...')
        lg.info('Sending get to: ' + self.HOST)
        response = self.user.getSession().get(self.HOST)
        self.subject_list = self.search_subjects(response)
        self.user.set_subjects(self.subject_list)

    def search_subjects(self, response):
        lg.info('Generating BeautiulSoup instance...')
        self.bs = BS(response.text, 'html.parser')
        lg.info('DONE')
        subjects = {}
        for a in self.bs.find_all('a', {'href': re.compile(r"https://egela1718.ehu.eus/course/view*")}):
            if a.has_attr('class'):
                subjects[a.get('href')] = a.text.lstrip()
        return subjects


    def load_subjects_menu(self):
        pass


if __name__ == '__main__':
    pass