#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import urllib
import urllib2
import config
from random import randint


# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

BASE_URL = 'https://api.telegram.org/bot' + config.TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        message = body['message']
        message_id = message.get('message_id')
        text = message.get('text')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == 'help':
                reply('Escribe /chistaco y recibe un chiste. Que te haga gracia o no ya es cosa tuya...')
            elif text == '/chistaco':
                chistes = [
                    u"Van dos y se cae el del medio",
                    u"- Camarero! Hay un mosca en sopa!\n- No es UN mosca, es UNA mosca.\n- Caray, qué vista tener usted!",
                    u"- Mamá, ¿qué haces en frente de la computadora con los ojos cerrados?\n- Nada, hijo, es que Windows me dijo que cerrara las pestañas...",
                    u"Le dice una madre a su hijo:\n- ¡Me ha dicho un pajarito que te drogas!\n- ¡La que se droga eres tu que hablas con pajaritos!",
                    u"- Papá, ¿qué se siente tener un hijo tan guapo?.\n- No sé hijo, pregúntale a tu abuelo...",
                    u"Dos amigos:\n- Oye, pues mi hijo en su nuevo trabajo se siente como pez en el agua.\n- ¿Qué hace? \n- Nada...",
                    u"- A ella le gusta la gasolina...\n- Oye, ¿no puedes cantar algo más educativo?\n- A ella le gusta la mezcla de hidrocarburos derivados de petróleo..."
                ]
                chosenjoke = randint(0,len(chistes))
                reply(chistes[chosenjoke])
                setEnabled(chat_id, True)


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
