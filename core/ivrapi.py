import kookoo
from db import models
from google.appengine.api import urlfetch
from xml.etree import ElementTree as etree
from twilio.rest import TwilioRestClient
import random
import sms
from datetime import datetime,timedelta
from google.appengine.ext import deferred
import os
import urllib
# call_config = {
#                 'kookoo':{
#                         'api_key':'KKb9c29f33223d0fcbf914af8c7ccca3ab',
#                         'url':'http://www.kookoo.in/outbound/outbound.php?api_key=%s&url=%s&phone_no=%s&callback_url=%s',
#                         'dndurl': 'http://www.kookoo.in/outbound/checkdnd.php?phone_no=%s'
#                         },
#                 'twilio':{
#                       'account_sid':"AC3f4b81e48c0772be741d576798473962",
#                       'auth_token':"7430278bd31caa1f3dea56c3f4f49057"
#                       },
#                 'callback_url':'http://%s/status-callback?voice=ec1.wav&api=%s',
#                 'voice_url':"http://%s/voice-playback?voice=ec1.wav&api=%s"
#               }
if os.getenv('HTTP_HOST', '').startswith('easyconnect-production'):
    account_sid = "AC3f4b81e48c0772be741d576798473962"
    auth_token = "7430278bd31caa1f3dea56c3f4f49057"
    apikey = 'KKb9c29f33223d0fcbf914af8c7ccca3ab'
    mobile_from_twilio = '+918033512343'
    mobile_from_kookoo = '918033512343'
    sms_prefix = ''
else:
    account_sid = "AC997b96a30773db043a91948953629a45"
    auth_token = "48a9b7725a7c59301176821a155d06c0"
    apikey = 'KKd1a4f4f7443412a34841727bff2514df'
    mobile_from_twilio = '+918049202255'
    mobile_from_kookoo = '918049202255'
    sms_prefix = '[Staging] - '

class CallApi(object):
    """
    Simple Class to execute a call
    """
    def __init__(self,host,voice='ec1.wav'):
        """
        Initialize class constructor with host param

        :param host: populate url with appropiate based on local development or appengine server

        :param voice: voice file name to be played when user answer the call.

        """
        self.host = host
        self.voice_url = "https://%s/voice-playback?voice=%s"%(host,voice)
        self.callback_url = "https://%s/status-callback"%host
        self.dndurl = 'http://www.kookoo.in/outbound/checkdnd.php?phone_no=%s'
        self.retry_callback_url = "https://%s/retry-status-callback"%host

    def check_dnd(self,mobileno):
        """
        Helper method to check if no. is in dnd
        """
        resp = urlfetch.fetch(url=self.dndurl%mobileno,deadline=60)
        xml_response = etree.fromstring(resp.content)
        message = xml_response.find('message').text
        return message.strip()

    def update_calllog(self,cid,to_mobile,from_mobile,api,num_type,member_id,member_name,broadcast_id):
        """
        Update Calllog when the first call has been made

        :param cid: Unique call id received to uniquely identify each call
        :param to_mobile: mobile no to call to
        :param from_mobile: mobile no. used
        :param api: api used to call the number ie. twilio or kookoo
        :param num_type: Mobile no. is regular no. or DND
        :param member_id: Member_id of the member called
        :param member_name: Member Name of the member called

        """
        call_log = models.CallLog(cid=cid,
                broadcastid = broadcast_id,
                member_id=member_id,
                member_name=member_name,
                mobile_number=to_mobile,
                voicemessage_url=self.voice_url,
                call_duration=0,
                start_time = None,
                phone_no_type=num_type,
                end_time = None,
                from_phone=from_mobile,
                voiceapi=api,
                voiceapi_status='queued',
                status="queued",
                retries = 1
                )
        call_log.put()
        return call_log

    def place_call(self,to_mobile,from_mobile,member_id,member_name,broadcast_id,bstatus='in-progress'):
        """
        function that calls the kookoo or twilio api for actual calls based on whether no. is in DND or not.

        :param to_mobile: mobile no to call to
        :param from_mobile: mobile no. used
        :param member_id: Member_id of the member called
        :param member_name: Member Name of the member called
        """
        dnd_resp = self.check_dnd(to_mobile)
        if dnd_resp == 'NON-DND':
            from_mobile = mobile_from_kookoo
            api = 'kookoo'
            num_type='Regular'
            if bstatus == 'in-progress':
                cid = KookooCall().call(to_mobile,self.voice_url,self.callback_url)
                if cid.strip().startswith("Max"):
                    deferred.defer(retry_kookoo,self.host,self.voice_url,to_mobile,from_mobile,
                                    member_id,member_name,broadcast_id,bstatus,_countdown=30)
                    return
            else:
                cid = str(random.randint(1000000, 9999999))
        else:
            api = 'twilio'
            from_mobile = mobile_from_twilio
            num_type='DND'
            if bstatus == 'in-progress':
                cid = TwilioCall().call(to_mobile,from_mobile,self.voice_url,self.callback_url)
            else:
                cid = str(random.randint(1000000, 9999999))

        call_log = self.update_calllog(cid,to_mobile,from_mobile,api,num_type,member_id,member_name,broadcast_id)
        if bstatus == 'auto-paused':
            run_task_at = datetime.now() + timedelta(minutes=15)
            call_log.next_try = run_task_at
            call_log.put()
            models.RetryTask.add_retry_task(call_log,run_task_at)

    def update_retry_calls(self,call_log_id,cid):
        # update call log and retry_tasks status
        retry_task = models.RetryTask.all().filter('call_log_id =',call_log_id)[0]
        retry_task.cid = cid
        retry_task.status = 'queued'
        retry_task.put()

        callog = models.CallLog.get_by_id(int(call_log_id))
        callog.cid = cid
        callog.status = 'queued'
        callog.put()

    def retry_call(self,to_mobile,from_mobile,voice_url,call_log_id):
        """
        function that retry calls using kookoo or twilio

        :param to_mobile: mobile no to call to
        :param from_mobile: mobile no. used
        :param voice_url: url that gets called when phone is answered
        :param call_log_id: calllog id to update the respective row in the CallLog table

        """
        dnd_resp = self.check_dnd(to_mobile)
        if dnd_resp == 'NON-DND':
            api = 'kookoo'
            num_type='Regular'
            k = KookooCall()
            cid = k.call(to_mobile,voice_url,self.retry_callback_url)
            if cid.startswith('Max'):
                capi = CallApi(self.host)
                deferred.defer(capi.retry_call,to_mobile,from_mobile,voice_url,call_log_id,_countdown=30)
                return
        else:
            api = 'twilio'
            num_type='DND'
            cid = TwilioCall().call(to_mobile,from_mobile,voice_url,self.retry_callback_url)
        self.update_retry_calls(call_log_id,cid)


def retry_kookoo(host,voice_url,to_mobile,from_mobile,member_id,member_name,broadcast_id,bstatus):
    vurl = voice_url.split("=")[-1]
    call = CallApi(host,voice=vurl)
    call.place_call(to_mobile,from_mobile,member_id,member_name,broadcast_id,bstatus)

class KookooCall(object):
    """
    Kookoo wrapper class that handles calls to kookoo api
    """
    def __init__(self):
        self.apikey = apikey
        self.rest_url = '''http://www.kookoo.in/outbound/outbound.php?api_key=%s&outbound_version=2&url=%s&phone_no=%s&caller_id=%s&callback_url=%s'''
        self.api = 'kookoo'

    def call(self,to_mobile,voice_url,callback_url):
        """
        function to execute api call to kookoo

        :param to_mobile: mobile no to call to

        :param voice_url: Url that will be called when user answered the call
        :param callback_url: Url that will be called when the call is ended

        :returns: call id that uniquely identify a call
        """
        #prepare voice and call back url append api name to urls so that we can track which api was used in call.
        vurl = voice_url+",%s"%self.api
        callback_url += "?api=%s"%self.api

        to_mobile = "0"+to_mobile # add 0 to mobile no. as kookoo does not recognize no.
        kookoo_url = self.rest_url%(self.apikey,vurl,to_mobile,mobile_from_kookoo,callback_url)
        response = urlfetch.fetch(url=kookoo_url,deadline=60)
        xml_response = etree.fromstring(response.content)
        status = xml_response.find('status').text
        message = xml_response.find('message').text
        # return call sid for updating call log
        return message

class TwilioCall(object):
    """
    Twilio Wrapper class
    """
    def __init__(self):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.api = 'twilio'

    def call(self,to_mobile,from_mobile,voice_url,callback_url,**kwargs):
        """
        function to execute api call to twilio

        :param to_mobile: mobile no to call to
        :param from_mobile: mobile no. used
        :param voice_url: Url that will be called when user answered the call
        :param callback_url: Url that will be called when the call is ended

        :returns: call id that uniquely identify a call
        """
        #prepare voice and call back url append api name to urls so that we can track which api was used in call.
        voice_url += ",%s"%self.api
        callback_url += "?api=%s"%self.api
        to_mobile = "+91"+to_mobile # prepend +91 to mobile no.
        if kwargs:
            callback_url += '&%s'%urllib.urlencode(kwargs)
        client = TwilioRestClient(self.account_sid,self.auth_token)
        call = client.calls.create(url=voice_url,
                    status_callback = callback_url,
                    to=to_mobile,
                    method="GET",
                    from_=mobile_from_twilio)
        # return call sid for updating call log
        return call.sid

    def get_call_resource(self,call_sid):
        client = TwilioRestClient(self.account_sid,self.auth_token)
        resource = client.calls.get(call_sid)
        return resource

    def get_recording_resource(self,call_sid):
        client = TwilioRestClient(self.account_sid,self.auth_token)
        recording = client.recordings.get(call_sid)
        return recording

    def update_call_resource(self,call_sid,cstatus):
        client = TwilioRestClient(self.account_sid,self.auth_token)
        client.calls.update(call_sid,status=cstatus)

    def update_call_url(self,call_sid,vurl):
        client = TwilioRestClient(self.account_sid,self.auth_token)
        client.calls.update(call_sid,url=vurl,method="GET")

class SendMessage(object):
    admin_mobile_no = '9535332326'

    def __init__(self):
        pass

    def send_brodcast_msg(self,mobile_nos,msg):
        try:
            for mobile_number in mobile_nos:
                response, msg = sms.SmsService().send(mobile_number,message=msg)
                print response
        except Exception,e:
            print e

    def get_member_mobile(self,account,group):
        member_ids = [account.account_admin_member_id]
        if group.group_admin_member_id:
          member_ids.append(group.group_admin_member_id)
        if group.group_moderators:
          member_ids= member_ids+group.group_moderators.split(",")
        member_ids = list(set(member_ids))
        members = models.Members.get_members_by_ids(member_ids)
        mobile_no = []
        for m in members:
            mobile_no.append(m.mobile_number)
        return mobile_no


    def get_broadcast_created_msg(self,account,group,broadcastid,member_name):
        try:

            isttime = datetime.now() + timedelta(hours=5,minutes=30)
            mobile_no = self.get_member_mobile(account,group)
            msg = '''%(prefix)sNew Voice Broadcast created for \n %(account_name)s - %(group_name)s by %(member_name)s
                        on %(timestamp)s Broadcast Txn Id:%(broadcast_id)s'''%{'account_name':account.name,
                                                                                'group_name':group.name,
                                                                                'member_name':member_name,
                                                                                'timestamp':isttime.strftime("%d/%b/%Y %I:%M %p"),
                                                                                'broadcast_id':broadcastid,
                                                                                'prefix':sms_prefix
                                                                                }
        except Exception,e:
            print e
        return mobile_no,msg

    def get_broadcast_end_msg(self,account,group,broadcast,member_name):
        mobile_no = self.get_member_mobile(account,group)
        start = broadcast.start_date_time+timedelta(hours=5,minutes=30)
        if broadcast.end_date_time:
            end = broadcast.end_date_time+timedelta(hours=5,minutes=30)
        else:
            end = start

        msg = """%(prefix)sVoice Broadcast completed for %(account_name)s - %(group_name)s by %(member_name)s \r\n
                    Started: %(start_time)s \n
                    Ended: %(end_time)s \n
                    Txn ID: %(broadcast_id)s \n
                    Calls attempted: %(total_members)d \n
                    Calls answered: %(total_answered)d \n
                    Broadcast cost: Rs.%(total_cost).2f \n
                    Balance: Rs.%(balance).2f
                """%{'account_name':account.name,'group_name':group.name,'member_name':member_name,
                      'start_time':start.strftime("%d/%b/%Y %I:%M %p"),
                      'end_time':end.strftime("%d/%b/%Y %I:%M %p"),
                      'broadcast_id':str(broadcast.key.id()),
                      'total_members':broadcast.total_members,
                      'total_answered':broadcast.total_answered_regular+broadcast.total_answered_dnd,
                      'total_cost':broadcast.total_cost_rs,
                      'balance':account.balance,
                      'prefix':sms_prefix
                      }

        return mobile_no,msg

    def get_account_recharged_msg(self,account,recharge):
        msg = """%(prefix)sEasyConnect Recharge successful! Rs.%(amount)d has been
                 added to your Account: %(account_name)s
                 current Balance: Rs.%(balance)d."""%{
                                                    'amount':recharge,
                                                    'account_name':account.name,
                                                    'balance':account.balance,
                                                    'prefix':sms_prefix
                                                }
        return msg

    def ticket_created_msg(self,phone_no,name):
        current_time = datetime.now().strftime("%d/%b/%Y %I:%M %p")
        msg = """%(prefix)sNew Support Ticket Created\n
                 Date: %(dt)s \n
                 Mobile: %(phone_no)s \n
                 Name: %(name)s"""%{'prefix':sms_prefix,
                                    'dt':current_time,
                                    'phone_no':phone_no,
                                    'name':name}
        return msg
