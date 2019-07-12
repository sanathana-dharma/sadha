
import kookoo
import logging
import random
from db import models
from google.appengine.api import urlfetch
from xml.etree import ElementTree as etree

def easy_connect_ivr(caller_id, caller_phone, url):
  r = kookoo.Response()
  r.addPlayText('Welcome to Easy Connect!')
  r.addHangup()
  return r

_API_KEY = 'KKb9c29f33223d0fcbf914af8c7ccca3ab'
_kOOKOO_URL = 'http://www.kookoo.in/outbound/outbound.php?api_key=%s&url=%s&phone_no=%s&callback_url=%s'
_APPLICATION_URL = 'https://induj-easyconnect2.appspot.com/ivr?member_id=%s'
_VOICE_MSG = 'http://suryakiran.com/voice/audio/ec1.wav'
_CALL_BACK_URL = 'https://induj-easyconnect2.appspot.com/ivr_callback?member_id=%s'
KOOKOO_SUCCESS_CODE = 200
KOOKOO_EROR_CODE = 404

class KooKooError(Exception):
  pass

class IvrService(object):
  """Base class to make a call to the kookoo or twellio ivr."""


  DND_URL = 'http://www.kookoo.in/outbound/checkdnd.php?phone_no=%s'

  @classmethod
  def call(cls, mobile_number, member_id=None):
    message = ''
    if not member_id:
      member_id = random.randint(1000000, 9999999)
    try:
      dnd_url = cls.DND_URL % mobile_number
      logging.info('Fetching dnd Status.....')
      dnd_response = urlfetch.fetch(url=dnd_url,payload=None,method=urlfetch.GET)
      logging.info(dnd_response.content)
      dnd_xml_tree = etree.fromstring(dnd_response.content)
      message = xml_response.find('message').text
    except:
      logging.info('Error in fetching DND status')

    if message != 'NON-DND':
        logging.info('Placing call using Kokoo...')
        KooKooOutBound().place_voice_call(mobile_number, member_id)
    elif message == 'DND':
      models.CallLogs.add_log(
          mobile_number, member_id, message, 'Mobile no is registered for DND', True)
      pass # Needs to initialize twellio class to handle the DND numbers.

class KooKooOutBound(object):
  """The class is responsible to interact with kookoo api to place a call to the
  given mobile number."""
  def __init__(self):
    self._app_url = _APPLICATION_URL
    self._kookoo_url = _kOOKOO_URL
    self._callback_url = _CALL_BACK_URL 


  def place_voice_call(self, mobile_number, member_id):
    app_url = self._app_url % member_id
    callback_url = self._callback_url % member_id
    self._kookoo_url = self._kookoo_url % (_API_KEY, app_url, mobile_number, callback_url)
    logging.info('Kookoo url %s', self._kookoo_url)
    kookoo_response = None
    error = False
    try:
      kookoo_response = urlfetch.fetch(url=self._kookoo_url, payload=None, method=urlfetch.GET)
      logging.info(str(kookoo_response.content))
    except:
      msg = 'Kookoo failed to place the call.'
      logging.error(msg)
      models.CallLogs.add_log(member_id, mobile_number, 'APIERROR', msg)
      error = True
    if kookoo_response:
      xml_response = etree.fromstring(kookoo_response.content)
      status = xml_response.find('status').text
      message = xml_response.find('message').text
      status_code = kookoo_response.status_code
      self.add_call_log(member_id, mobile_number, status, message, status_code)
      if status == 'error' or status_code == KOOKOO_EROR_CODE:
        error = True
    if error:
      logging.info('Call Failed for mobile number %s', mobile_number)
      raise KooKooError('Call Failed')


  def add_call_log(self, member_id, mobile_number, status, message, status_code):
    if status_code == KOOKOO_SUCCESS_CODE:
      models.CallLogs.add_log(member_id, mobile_number, status, message)
    elif status_code == KOOKOO_EROR_CODE:
      models.CallLogs.add_log(member_id, mobile_number,
          'APIERROR', 'Voice Gateway Not available.')


class NewCallEventHandler(object):
  def __init__(self, cid, called_from_number, outbound_sid,
               cid_type, circle, operator, member_id):
    self.cid = cid
    self.called_from_number = called_from_number
    self.outbound_sid = outbound_sid
    self.cid_type = cid_type
    self.circle = circle
    self.operator = operator
    self.member_id = member_id
    
  def get_response(self):
    models.CallLogs.update_status(self.member_id, 'Call in Progress')
    response = kookoo.Response()
    response.addPlayAudio(_VOICE_MSG)
    response.addHangup()     
    logging.debug("Voice message played, ending call!")
    return response

class DTMFEventHandler(object):
  def __init__(self, cid, called_from_number, outbound_sid,
               cid_type, circle, operator, member_id=None):
    self.cid = cid
    self.called_from_number = called_from_number
    self.outbound_sid = outbound_sid
    self.cid_type = cid_type
    self.circle = circle
    self.operator = operator
    self.member_id = member_id
    
  def get_response(self): pass


class RecordingEventHandler(object):
  def __init__(self, cid, called_from_number, outbound_sid,
               cid_type, circle, operator, member_id=None):
    self.cid = cid
    self.called_from_number = called_from_number
    self.outbound_sid = outbound_sid
    self.cid_type = cid_type
    self.circle = circle
    self.operator = operator
    self.member_id = member_id

  def get_response(self):pass


class DisconnectEventHandler(object):
  def __init__(self, cid, called_from_number, outbound_sid,
               cid_type, circle, operator, member_id=None):
    self.cid = cid
    self.called_from_number = called_from_number
    self.outbound_sid = outbound_sid
    self.cid_type = cid_type
    self.circle = circle
    self.operator = operator
    self.member_id = member_id

  def get_response(self):
    models.CallLogs.update_status(self.member_id, 'Completed')


class VoiceCallResponse(object):
  event_handlers = {
    'Record': RecordingEventHandler, 'NewCall': NewCallEventHandler,
    'GOTDTMF': DTMFEventHandler,'Disconnect': DisconnectEventHandler
  }
 

  @classmethod
  def get_handler(cls, event, cid, called_from_number, outbound_sid, cid_type, circle, operator, member_id):
    if event in cls.event_handlers:
      handler = cls.event_handlers.get(event)
      return handler(cid, called_from_number, outbound_sid, cid_type, circle, operator, member_id)