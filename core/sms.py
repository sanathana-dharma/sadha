import urllib
import logging

_USER = 'kiran@suryakiran.com'
_PASWD = 'goblan389'
_DEFAULT_MSG = 'This is Test message'

class SmsService(object):
  def __init__(self, user=_USER, password=_PASWD):
    self.user = user
    self.password = password
    self.url = 'http://api.mvaayoo.com/mvaayooapi/MessageCompose?'
    self.state = '4'
    self.dcs = '0'

  def send(self, number, message=_DEFAULT_MSG):
    param = {}
    param['user'] = self.user + ":" + self.password
    param['senderID'] = "TEST SMS"
    param['receipientno'] = number
    param['dcs'] = self.dcs
    param['msgtxt'] = message
    param['state'] = self.state
    url = self.url + (urllib.urlencode(param))
    api_response = ''

    try:
      response = urllib.urlopen(url).read()
      api_response = response.split(',')[1]
    except Exception,e:
        print e

    return api_response, message

