# -*- coding: UTF-8 -*-

import httplib
import json
import os
import urllib
import httplib2
import logging
import random
import time
import hmac
import binascii
import hashlib

import jinja2
import webapp2
from webapp2_extras import sessions
from bs4 import BeautifulSoup
from datetime import datetime,timedelta

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

egela_cookie=''
fechaPublicar=''
cursoPublicar=''
enlaceCurso=''
html=''

app_id='elevated-bonito-163807'
#google credendiales
cliente_id="870961824121-6k73sb9kuq2ouqsthpdms5qda3rsra45.apps.googleusercontent.com"
cliente_secret="4qYw4xT-8P0JpqoNwzJd3wG9"
redirect_uri="http://" + app_id + ".appspot.com/callback_uri"

#Twitter credenciales

callback_url = 'https://' + app_id + '.appspot.com/oauth_callback'

consumer_key = 'mmcXZWXbw3tNAZ5WdiuSgxwJ4'
consumer_secret = 'yZUP6wK3YanhhHHXfF9vmNgCjvIyPOZhL8dXbeVcpzkRg2audy'

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()


config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'my-super-secret-key'}


class MainHandler(webapp2.RequestHandler):
    def get(self):
        #self.response.write('<a href="/LoginAndAuthorize">Login ant Authorize with Calendar</a>')
        self.redirect('/html/Formulario.html')

class LoginAndAuthorizeCalendar(BaseHandler):
    def get(self):
        servidor = 'accounts.google.com'
        conn = httplib.HTTPSConnection(servidor)
        conn.connect()
        metodo = 'GET'
        params = {'client_id': cliente_id,
                  'redirect_uri': redirect_uri,
                  'response_type': 'code',
                  'scope': 'https://www.googleapis.com/auth/calendar',
                  'approval_prompt': 'auto',
                  'access_type': 'offline'}
        params_coded = urllib.urlencode(params)
        uri = '/o/oauth2/v2/auth' + '?' + params_coded
        self.redirect('https://' + servidor + uri)

        logging.debug(params)

class LoginAndAuthorizeTwitter(BaseHandler):

    def get(self):
        logging.debug('ENTERING LoginAndAuthorize --->')
        http = httplib2.Http()
        method = 'POST'
        url = 'https://api.twitter.com/oauth/request_token'
        oauth_headers = {'oauth_callback': callback_url}
        goiburuak = {'User-Agent': 'Google App Engine',
                     'Authorization': createAuthHeader(method, url, oauth_headers, None, None)}
        respuesta, content = http.request(url, method, headers=goiburuak)
        if respuesta['status'] != '200':
            logging.debug('/oauth/request_token != 200')
        logging.debug(content)

        oauth_callback_confirmed = content.split('&')[2].replace('oauth_callback_confirmed=', '')
        if oauth_callback_confirmed != 'true':
            logging.debug('oauth_callback_confirmed != true')

        self.session['oauth_token'] = content.split('&')[0].replace('oauth_token=', '')
        self.session['oauth_token_secret'] = content.split('&')[1].replace('oauth_token_secret=', '')

        base_url = 'https://api.twitter.com/oauth/authenticate'
        params = {'oauth_token': self.session.get('oauth_token')}
        params = urllib.urlencode(params)
        request_url = base_url+"?"+params
        self.redirect(request_url)


class OAuthHandler(BaseHandler):
    def get(self):
        logging.debug("Entendo en OAuthHandler")
        servidor = 'accounts.google.com'
        metodo = 'POST'
        uri = '/o/oauth2/token'
        auth_code = self.request.get('code')
        params = {'code': auth_code,
                  'client_id': cliente_id,
                  'client_secret': cliente_secret,
                  'redirect_uri': redirect_uri,
                  'grant_type': 'authorization_code'}
        params_encoded = urllib.urlencode(params)
        cabeceras = {'Host': servidor,
                     'User-Agent': 'Youtube Python bezeroa',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Content-Length': str(len(params_encoded))}
        http = httplib2.Http()
        respuesta, cuerpo = http.request('https://' + servidor + uri, method=metodo, headers=cabeceras,
                                         body=params_encoded)

        jsoncuerpo = json.loads(cuerpo)
        access_token = jsoncuerpo['access_token']
        self.session['access_token'] = access_token

        self.redirect('/html/Enviar_Calendar.html')

class OAuthHandlerTwitter(BaseHandler):

    def get(self):
        logging.debug('ENTERING OAuthHandler --->')
        oauth_token = self.request.get('oauth_token')
        oauth_verifier = self.request.get('oauth_verifier')
        if oauth_token != self.session.get('oauth_token'):
            logging.debug('step2_oauth_token != step1_oauth_token')

        http = httplib2.Http()
        method = 'POST'
        url = 'https://api.twitter.com/oauth/access_token'
        oauth_headers = {'oauth_token': oauth_token}
        params = {'oauth_verifier': oauth_verifier}
        cuerpo = urllib.urlencode(params)
        cabeceras = {'User-Agent': 'Google App Engine',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Content-Length': str(len(cuerpo)),
                     'Authorization': createAuthHeader(method, url, oauth_headers, params, self.session.get('oauth_token_secret'))}
        respuesta, content = http.request(url, method, headers=cabeceras, body=cuerpo)
        logging.debug(respuesta['status'])
        logging.debug(content)

        self.session['oauth_token'] = content.split('&')[0].replace('oauth_token=', '')
        self.session['oauth_token_secret'] = content.split('&')[1].replace('oauth_token_secret=', '')
        self.session['twitter_user'] = content.split('&')[3].replace('screen_name=', '')

        self.redirect('/html/Enviar_Twitter.html')


class Calendar(BaseHandler):
    def post(self):
        access_token = self.session.get('access_token')
        logging.debug('hola')
        servidor = 'www.googleapis.com'
        metodo = 'POST'
        uri = '/calendar/v3/calendars/deiroyo@gmail.com/events'
        parametros = {'start': {
            'dateTime': '2017-05-22T09:00:00-07:00',
            'timeZone': 'Europe/Madrid',
        },
            'end': {
                'dateTime': '2017-05-23T12:00:00-07:00',
                'timeZone': 'Europe/Madrid',
            },
            'summary': 'prueba',
            'description': 'hola'

        }
        cuerpo = json.dumps(parametros)
        cabeceras = {'User-Agent': 'Python Client',
                     'Host': servidor,
                     'Authorization': 'Bearer ' + access_token,
                     'Content-Length': str(len(cuerpo)),
                     'Content-Type': 'application/json'
                     }
        http = httplib2.Http()
        respuesta, cuerpo = http.request('https://' + servidor + uri, method=metodo, headers=cabeceras,body=cuerpo)

        logging.debug(respuesta)
        logging.debug(cuerpo)
        self.redirect('/html/Formulario.html')

class Twitter(BaseHandler):

    def post(self):
        logging.debug('ENTERING Twitter --->')
        oauth_token = self.session['oauth_token']
        oauth_token_secret = self.session['oauth_token_secret']

        #mensaje = self.request.get('mensaje')
        mensaje='adios'
        http = httplib2.Http()
        method = 'POST'
        base_url = 'https://api.twitter.com/1.1/statuses/update.json'
        oauth_headers = {'oauth_token': oauth_token}
        params = {'status': mensaje}
        cuerpo = urllib.urlencode(params)
        cabeceras = {'User-Agent': 'Google App Engine',
                     'Content-Type': 'application/x-www-form-urlencoded',
                     'Content-Length': str(len(cuerpo)),
			         'Authorization': createAuthHeader(method, base_url, oauth_headers, params, oauth_token_secret)}
        respuesta, content = http.request(base_url, method, headers=cabeceras, body=cuerpo)
        logging.debug(respuesta['status'])
        logging.debug(content)
        self.redirect('/html/Formulario.html')
        #self.redirect('/') redirigir a algun lado


def createAuthHeader(method, base_url, oauth_headers, request_params, oauth_token_secret):
    logging.debug('ENTERING createAuthHeader --->')
    oauth_headers.update({'oauth_consumer_key': consumer_key,
                          'oauth_nonce': str(random.randint(0, 999999999)),
                          'oauth_signature_method': "HMAC-SHA1",
                          'oauth_timestamp': str(int(time.time())),
                          'oauth_version': "1.0"})
    oauth_headers['oauth_signature'] = \
            urllib.quote(createRequestSignature(method, base_url, oauth_headers, request_params, oauth_token_secret), "")

    if oauth_headers.has_key('oauth_callback'):
        oauth_headers['oauth_callback'] = urllib.quote_plus(oauth_headers['oauth_callback'])
    authorization_header = "OAuth "
    for each in sorted(oauth_headers.keys()):
        if each == sorted(oauth_headers.keys())[-1]:
            authorization_header = authorization_header \
                                 + each + "=" + "\"" \
                                 + oauth_headers[each] + "\""
        else:
            authorization_header = authorization_header \
                                 + each + "=" + "\"" \
                                 + oauth_headers[each] + "\"" + ", "

    return authorization_header


def createRequestSignature(method, base_url, oauth_headers, request_params, oauth_token_secret):
    logging.debug('ENTERING createRequestSignature --->')
    encoded_params = ''
    params = {}
    params.update(oauth_headers)
    if request_params:
        params.update(request_params)
    for each in sorted(params.keys()):
        key = urllib.quote(each, "")
        value = urllib.quote(params[each], "")
        if each == sorted(params.keys())[-1]:
            encoded_params = encoded_params + key + "=" + value
        else:
            encoded_params = encoded_params + key + "=" + value + "&"

    signature_base = method.upper() + \
                   "&" + urllib.quote(base_url, "") + \
                   "&" + urllib.quote(encoded_params, "")

    signing_key = ''
    if oauth_token_secret == None:
        signing_key = urllib.quote(consumer_secret, "") + "&"
    else:
        signing_key = urllib.quote(consumer_secret, "") + "&" + urllib.quote(oauth_token_secret, "")

    hashed = hmac.new(signing_key, signature_base, hashlib.sha1)
    oauth_signature = binascii.b2a_base64(hashed.digest())

    return oauth_signature[:-1]




class Egela (BaseHandler):
    def post(self):
        servidor = 'egela1617.ehu.eus'
        conn = httplib.HTTPSConnection(servidor)
        conn.connect()
        self.session['clase']='Egela'


        metodo = 'POST'
        usuario=self.request.get('user')
        password = self.request.get('pass')
        print usuario
        print password

        try:
            params = {'username': 'droyo002',
                      'password': 'ASdf1234'}
            params_encoded = urllib.urlencode(params)
            recurso = '/login/index.php'
            cabeceras_peticion = {'Host': servidor,
                                  'Content-Type': 'application/x-www-form-urlencoded',
                                  'Content-Length': str(len(params_encoded))
                                  }
        except:
            print 'problem'


        conn.request(metodo, recurso, headers=cabeceras_peticion, body=params_encoded)
        respuesta=conn.getresponse()
        logging.debug(respuesta.status)
        #self.response.out.write(respuesta.getheaders())

        cookie = respuesta.getheader('set-cookie')
        cookie2 = cookie.split(';')
        print cookie2
        global egela_cookie
        egela_cookie = cookie2[0]
        self.session['cookie'] = egela_cookie
        print egela_cookie

        servidor = 'egela1617.ehu.eus'
        conn = httplib.HTTPSConnection(servidor)
        conn.connect()

        metodo = 'GET'
        recurso = '/my/'
        cabeceras_peticion = {'Host': servidor,
                              'cookie': egela_cookie
                               }
        cuerpo_peticion = ''

        conn.request(metodo, recurso, headers=cabeceras_peticion, body=cuerpo_peticion)

        response = conn.getresponse()
        print response.status
        if (response.status!=200):
            time.sleep(2)
            self.redirect('/buscarCookie')
        global html
        html = BeautifulSoup(response.read(), "html.parser")
        lista = ['lista']
        n = 1
        print html.find_all('h2')

        for enlace in html.find_all('h2'):
            try:
                #lista1.insert ( str(n) + ') ' + enlace.a.text+'\n')
                time.sleep(1)
                lista.insert(n, enlace.a.text)

                n = n + 1


            except:
                print 'problem'

        #numeroCurso = raw_input("Introduce el numero del curso: ")
        template_values = {'nombre': lista}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        time.sleep(2)
        #self.session['lista']=lista
        conn.close()


    def get(self):
        self.post()

class buscarCookie(BaseHandler) :
    def post(self):
        servidor = 'egela1617.ehu.eus'
        conn = httplib.HTTPSConnection(servidor)
        conn.connect()

        metodo = 'POST'
        usuario = self.request.get('user')
        password = self.request.get('pass')
        print usuario
        print password

        try:
            params = {'username': 'droyo002',
                      'password': 'ASdf1234'}
            params_encoded = urllib.urlencode(params)
            recurso = '/login/index.php'
            cabeceras_peticion = {'Host': servidor,
                                  'Content-Type': 'application/x-www-form-urlencoded',
                                  'Content-Length': str(len(params_encoded))
                                  }
        except:
            print 'problem'

        conn.request(metodo, recurso, headers=cabeceras_peticion, body=params_encoded)
        respuesta = conn.getresponse()
        print respuesta.status

        if (respuesta.status!=200) :
            clase=self.session['clase']
            self.redirect('/'+clase)
        cookie = respuesta.getheader('set-cookie')
        cookie2 = cookie.split(';')

        global egela_cookie
        egela_cookie = cookie2[0]
        self.session['cookie'] = egela_cookie


    def get(self):
       self.post()


class buscarCurso(BaseHandler):
    def post(self):
        self.session['clase'] = 'buscarCurso'
        #lista=self.session['lista']
        #numero=int(self.request.get('numero'))

        curso = 'Sistemas Web'
        #print curso

        for enlace in html.find_all('h2'):
            try:
                time.sleep(1)
                if (enlace.a.text == curso):

                    self.session['cursoPublicar'] = enlace.a.text
                    self.session['enlace'] =enlace.a.get('href')
                    print ('Encontrado')

            except:
                print 'problem'

        self.redirect('/fechas')



    def get(self):
        self.post()




        #sself.redirect('/html/cursos.html')



class fechas(BaseHandler):
    def get(self):

        self.session['clase'] = 'fechas'
        enlaceCurso = self.session['enlace']

        enlace = enlaceCurso.split('=')
        cookie = self.session['cookie']

        servidor = 'egela1617.ehu.eus'

        conn = httplib.HTTPSConnection(servidor)
        conn.connect()
        print enlace[1]
        metodo = 'GET'
        recurso = '/calendar/view.php?view=upcoming&course=' + enlace[1]
        cabeceras_peticion = {'Host': servidor,
                              'cookie': cookie
                               }


        conn.request(metodo, recurso, headers=cabeceras_peticion,body='')

        response = conn.getresponse()
        print response.status
        if response.status!=200:
            time.sleep(1)
            self.redirect('/buscarCookie')


        cursohtml = BeautifulSoup(response.read(), "html.parser")
        #print cursohtml
        print 'Buscando actividades pendientes'


        for enlace in cursohtml.find_all(attrs={'class': 'referer'}):
            try:

                print enlace.a.text

                time.sleep(1)
                enlaceActividad = enlace.a.get('href')
                self.session['enlaceActividad']=enlaceActividad
                self.redirect('/actividad')


            except:
                print 'problemas'
                clean = ''

        print'Se acabo de buscar actividades pendientes'
        conn.close()
        #respuesta, content = http.request('https://'+servidor+recurso, metodo, headers=cabeceras_peticion,body='')
        #logging.debug(respuesta['status'])
        #logging.debug(content)
        #self.redirect('/html/Formulario.html')

class actividad(BaseHandler):

    def post(self):

        self.session['clase'] = 'actividad'
        enlaceActividad=self.session['enlaceActividad']

        enlaceActividadFinal = enlaceActividad.split('/')
        print enlaceActividad[5]
        servidor = 'egela1617.ehu.eus'
        conn = httplib.HTTPSConnection(servidor)
        conn.connect()


        #print enlaceActividadFinal[5]
        metodo = 'GET'
        recurso = '/mod/assign/' + enlaceActividadFinal[5]

        cabeceras_peticion = {'Host': servidor,
                              'cookie': egela_cookie

                              }


        conn.request(metodo, recurso, headers=cabeceras_peticion)

        response = conn.getresponse()
        print response.status
        if response.status!=200:
            time.sleep(1)
            self.redirect('/buscarCookie')



        actividadhtml = BeautifulSoup(response.read(), "html.parser")
        n = 1
        print  actividadhtml.find_all('tr',attrs={'class': 'r0'})
        for enlace in actividadhtml.find_all('tr', attrs={'class': 'r0'}):
            try:
                time.sleep(1)
                if (n == 2):
                    fecha = str(enlace.find(attrs={'class': 'cell c1 lastcol'}).text)
                    print fecha
                    # parsear fecha

                    n = n + 1
                n = n + 1

            except:
                clean = ''

        conn.close()
    def get(self):
        self.post()

    def compararFechas(fecha):
        formato = "%Y %B %d %H:%M"

        hoy = datetime.today()
        fecha_hoy = hoy.strftime(formato)

        # sacar dia mes año
        fecha1 = fecha.split(',')
        semana = fecha1[1]
        semana1 = semana.split(' ')

        dia = str(semana1[1])
        mes = str(semana1[2])
        ano = str(semana1[3])

        # sacar la hora y minuto
        hora = fecha1[2]
        hora1 = hora.split(' ')
        hora2 = hora1[1].split(':')

        hora = str(hora2[0])
        minuto = str(hora2[1])

        unirfecha = str(ano + ' ' + mes + ' ' + dia + ' ' + hora + ':' + minuto)

        fecha_inicial = datetime.strptime(unirfecha, formato)
        fechaegela = fecha_inicial.strftime(formato)

        if (fecha_hoy <= fechaegela):
            global fechaPublicar
            fechaPublicar = fechaegela
            return True


class PostTwitter(BaseHandler) :
    def post(self):
        self.redirect('/html/Login_Twitter.html')

class PostCalendar(BaseHandler):
    def post(self):
        self.redirect('/html/Login_Calendar.html')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/LoginAndAuthorizeCalendar', LoginAndAuthorizeCalendar),
    ('/LoginAndAuthorizeTwitter', LoginAndAuthorizeTwitter),

    ('/Egela', Egela),
    ('/fechas', fechas),
    ('/buscarCurso', buscarCurso),
    ('/buscarCookie',buscarCookie),
    ('/actividad',actividad),

    ('/callback_uri', OAuthHandler),
    ('/oauth_callback', OAuthHandlerTwitter),

    ('/PostTwitter', PostTwitter),
    ('/PostCalendar', PostCalendar),

    ('/twitter', Twitter),
    ('/calendar', Calendar)], config=config, debug=True)
