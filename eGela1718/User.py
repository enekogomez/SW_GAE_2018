import requests as rs
import logging as lg

lg.basicConfig(format='%(asctime)s : %(levelname)s: %(message)s', level=lg.INFO)


class User:

    def __init__(self, identifier):
        self.subjects = None
        self.identifier = identifier
        try:
            self.session = rs.session()
        except rs.RequestException as e:
            print(e)

    def set_pass(self,password):
        self.password = password

    def set_subjects(self, subject_list):
        lg.info("Associating subjects to user...")
        self.subjects = subject_list
        lg.info("DONE")


    def get_username(self):
        return self.identifier

    def get_pass(self):
        return self.password

    def getSession(self):
        try:
            return self.session
        except self.session is None as e:
            print(e)

    def get_subject_list(self):
        return self.subjects
