import models
import logging
from google.appengine.api import urlfetch
from google.appengine.runtime import DeadlineExceededError
import urllib
import time 
import datetime
from datetime import timedelta
import gLib


'''
Created on Feb 22, 2014

@author: surya
'''
'''
This module will include mainly mappers which are responsible for delivery of broadcast messages
1. create callog records for a new broadcast
first time input: broadcast key
next time input: cursor
process: loop through members list of a group and create calllog records

2. place calls for a new broadcast
first time input: broadcast key
next time input: cursor
process: loop through calllogs of a SINGLE BROADCAST and place calls

3. for retrying incomplete broadcasts
first time: nothing
next time: cursor
process: loop through all available pending calllog records and place calls to them, calllogs are selected based on some spl logic
'''



'''
1. create callog records for a new broadcast
first time input: broadcast key
next time input: cursor
process: loop through members list of a group and create calllog records
'''



class boBM(object):
    """ BROADCAST MANAGER """
    def __init__(self):
        self._broadcastRec = None
        self._groupRec = None
        
    
    def create_helper_for_mapper_create_calllogs(self, broadcastKey):
        """ This is will create a dynamic custom object that holds values required for particular Mapper to run """
        broadcastRec = models.BROADCAST.get(broadcastKey)
        self._broadcastRec = broadcastRec 
        groupRec = models.GROUP.get(broadcastRec.parent_group.key())
        self._groupRec = groupRec 
                        
        o = boEmpty()
        o.broadcastKey = broadcastKey
        o.groupKey = broadcastRec.parent_group.key()
        
        logging.debug("inside create_helper_for_mapper_create_calllogs > self._broadcastRec =%s",self._broadcastRec)
        
        return o    
    
    def get_relevant_voicemessage(self, broadcastRec, memberLanguage):
        """ This will return a voice message rec/object of given broadcast record and specified language if available """
        lst = models.VOICEMESSAGE.gql("WHERE parent_broadcast = :1 AND msg_language = :2", broadcastRec, int(memberLanguage)).fetch(1)  
        voicemessageRec = lst[0]
        return voicemessageRec 
                
    def place_calls(self, c, member_mobile, raiseTimeout):
                        
        logging.debug("inside mapper_place_calls --> place_calls method")
        
        #Format Mobile number for KOOKOO (from 12 digit to 10 digit)
        member_mobile = gLib.format_mobile_number_kookoo(member_mobile)
                
        ErrorOccured = False        
        urlFetchResponseObj = None        
        callTID = ""    #the tracking ID provided by voice service provider to track our call
        
        #note: Call back from voice proivde (kookoo) is a POST response not GET
        sysURL = "http://induj-easyconnect1.appspot.com"
        kookooURL = "http://www.kookoo.in"
        ivrUrl = sysURL + "/ivr_voice_delivery"
        callbackURL = "http://www.suryakiran.com/voice/easyconnect/post2get.php"
        
        voiceURL = kookooURL +"/outbound/outbound.php?api_key=KKd1a4f4f7443412a34841727bff2514df&outbound_version=2"
        voiceURL = voiceURL + "&url=" + ivrUrl + "?calllog_key=" + str(c.key())
        voiceURL = voiceURL + "&callback_url=" + callbackURL
        voiceURL = voiceURL + "&phone_no=" + member_mobile
                            
        logging.debug("mapper_place_calls --> Final Fetch Voice URL: "+voiceURL)
        try:
            #urlFetchResponseObj = urlfetch.fetch(url=DictSMSapi['url'],payload=DictSMSapi['form_data'],method=urlfetch.POST)
            urlFetchResponseObj = urlfetch.fetch(url=voiceURL,payload=None,method=urlfetch.GET)            
        except:
            logging.critical("mapper_place_calls --> Aborting..Error while doing URLFetch")
            ErrorOccured = True
            BlnProceedFurther= False #No point in trying when URL fetch has failed
        
        logging.debug("mapper_place_calls --> URL Fetch successful, now lets check the Response code..")
        
        # Deal with Response
        if urlFetchResponseObj:
            if urlFetchResponseObj.status_code==200:
                #Success
                # the result in Kookoo could be
                # a) Queued
                # b) Error
                #lets log this                             
                logging.debug('mapper_place_calls --> place_calls --> Send Response ='+urlFetchResponseObj.content)                            
                urlResponse = str(urlFetchResponseObj.content)
                
                callStatus = self.get_xml_value(urlResponse, 'status')
                callStatusDesc = self.get_xml_value(urlResponse, 'message')
                                 
                #======================================================================================================
                # CRITICAL LOGIC
                # THE FLOW IS DIFFERENT WHEN CALLBACK OCCURS FOR CALLS THAT ARE FIRST-TIME VS THOSE BEING RE-TRIED
                #======================================================================================================
                
                
                #if c.try_count == 0:
                #    # Placing call first time                    
                #    c.try_count = 1
                #elif  c.try_count == 1:
                #    # Placing call 2nd time
                #    c.try_count = 2
                #elif  c.try_count == 2:
                #    # Placing call Third and final time
                #    c.try_count = 3                                
                c.try_count = c.try_count + 1 
                logging.debug("Updated trycount from %s to %s",c.try_count,c.try_count+1)
                
                #======================================================================================================
                # CRITICAL LOGIC
                # AT THIS STAGE, STATUS VALUES CAN BE: QUEUED OR ERROR  
                #======================================================================================================                
                if callStatus=="ERROR":
                    # FAILED TEMPORARILY OR PERMANENTLY
                    c.last_try_time = gLib.getDateTime()    # we update date now, because we wont retry again, or anytime soon
                    if callStatusDesc.find('DND') > 0:  
                        # DND CASE
                        c.call_status = "DND"
                        c.call_tid = None                
                        c.callback_status = "PHONE IN DND"
                        c.callback_status_desc = "WILL NOT TRY AGAIN"
                        
                    elif callStatusDesc.find('CALLS WILL NOT BE MADE') > 0:
                        # 9AM TO 9PM TRAI RULES
                        c.call_status = "RETRYING"
                        c.call_tid = None                
                        c.callback_status = "NON WORKING HOURS"
                        c.callback_status_desc = "CALLS CAN BE PLACED ONLY BETWEEN 9AM TO 9PM"
                    
                    elif callStatusDesc == "MAX CONNECTIONS REACHED":
                        # MAX CONNECTIONS REACHED, we need to retry later
                        c.call_status = "RETRYING"
                        c.call_tid = None                
                        c.callback_status = "MAX CONNECTIONS REACHED"
                        c.callback_status_desc = "MAX CONNECTIONS REACHED, WILL RETRY IN NEXT CRON"
                        
                    else:
                        # OTHER CASES SUCH AS CREDIT LIMIT EXCEEDED ETC.
                        c.call_status = "FAILED"
                        c.call_tid = None                
                        c.callback_status = callStatusDesc
                        c.callback_status_desc = callStatusDesc
                                                  
                elif callStatus=="QUEUED":
                    # CALL WAS QUEUED SUCCESSFULLY
                    c.call_status = callStatus
                    # This step is very critical, because TID will change every time a call is placed, 
                    # but our call log record will remain same
                    # so if we are retrying, then our call_tid needs to be updated once again
                    c.call_tid = callStatusDesc
                    c.callback_status = None # Clear old value of last attempt, if any                                                       
                    c.callback_status_desc = "Call was successfully queued.."
                    
                else:
                    # UNKNOWN CASE, LETS ABORT THIS CALL
                    c.call_status = "FAILED"
                    c.call_tid = None                
                    c.callback_status = callStatusDesc
                    c.callback_status_desc = callStatusDesc                    
                
                
                c.put()     
                BlnProceedFurther = True                  
                
                          
            elif urlFetchResponseObj.status_code==404:
                # Voice API not available
                c.call_status = 'APIERROR'
                c.call_tid = 'None'                  
                c.put()
                logging.debug('mapper_place_calls --> place_calls --> Voice Gateway Not available, continuing task chain')
                BlnProceedFurther= True                            
            else:
                ErrorOccured = True
                logging.debug("mapper_place_calls --> place_calls --> Unknown URLFetch Response Status Code: Aborting Task chain")
                BlnProceedFurther= False
        else:
            ErrorOccured = True
            BlnProceedFurther = False
            logging.debug("mapper_place_calls --> place_calls --> NUll Response for URLFetch, aborting task chain ")
        
        if ErrorOccured==True:
            #Log the error
            if urlFetchResponseObj:
                logging.error('mapper_place_calls --> place_calls --> urlFetchResponseObj=%s, urlFetchResponseObj.status_code=%s,urlFetchResponseObj.content=%s',urlFetchResponseObj,urlFetchResponseObj.status_code,urlFetchResponseObj.content)
            else:
                logging.error('mapper_place_calls --> place_calls --> Send Error - Voice API not responding..')
        else:
            #Send was Successful
            logging.debug("mapper_place_calls --> place_calls --> SUCCESS: Send was successful, no errors")    

        #raise Deadline error for testing
        if raiseTimeout:                    
            logging.debug("Raising sample DeadlineExceededError")
            raise DeadlineExceededError        
        
        if ErrorOccured ==True:
            logging.debug("Error Occurred, returning False")
            return False
        
        logging.debug("No Errors, returning True")
        return True
                                 
    def get_xml_value(self, strData, StrTag):
        s = strData.find('<'+StrTag+'>') + len('<'+StrTag+'>')
        en = strData.find('</'+StrTag+'>')
        return strData[s:en].upper()

    def deduct_balance(self, broadcastRec, deductAmount):
        """ This deducts certain balance from the Account to which this Broadcast belongs """
        self._broadcastRec = broadcastRec
        accountRec = broadcastRec.parent_account
        # Activate stock balance if any, before charging
        accountRec.activate_stock_balance()
        
        if deductAmount <= accountRec.balance1:
            # LETS DEDUCT
            accountRec.balance1 = accountRec.balance1 - deductAmount
            accountRec.put()  
            
            logging.debug("Deducted %s from Account Balance, New Balance = %s", deductAmount, accountRec.balance1)
                       
            broadcastRec.isBilled = True
            broadcastRec.total_amount = deductAmount
            broadcastRec.put()
            logging.debug("Updated Broadcast isBilled status to TRUE")            
            
            return True
        else:
            # THIS CAN'T HAPPEN, BUT ACCOUNT HAS LESS BALANCE AFTER BROADCAST IS COMPLETE
            logging.critical("Unable to Deduct %s from Account Balance, Current Balance = %s", deductAmount, accountRec.balance1)
            return False
            
        
    

    

def admin_task_compute_broadcast(broadcastRec):
    """ The actual code which works when the parent http url is executed """
            
    calllog_recs = models.CALLLOG.all()
    calllog_recs.filter('parent_broadcast =', broadcastRec)
    calllog_recs.order('call_status')
    
    total_duration_of_all_answered_calls = 0
    total_members_answered = 0
    total_members_tried = 0
    total_members_failed = 0
    total_members_dnd = 0
    total_members_others = 0
    
    #call units counter
    call_units_counter = 0
    
    
    # call duration = Length of the Voice Message (for now as we dont offer repeat function)
    lang_call_duration = 0 
    
    lstRecs = []
    for r in calllog_recs:
        logging.debug("mobile=%s, status=%s, lang=%s, r.call_duration=%s",r.member_mobile, r.call_status, r.lang, r.call_duration)
        total_members_tried = total_members_tried +1
            
        if r.call_status == "ANSWERED":                
            total_members_answered = total_members_answered +1
            
            #Calculate Call units 
            call_units_counter = call_units_counter + gLib.calculate_call_units(r.call_duration)                
            
            #Calculate call duration of all languages
            lang_call_duration = lang_call_duration + r.call_duration            
                
        elif r.call_status == "NOT-AVAILABLE":
            total_members_failed = total_members_failed + 1
            
        elif r.call_status == "DND":
            total_members_dnd = total_members_dnd + 1
                            
        else:
            total_members_others = total_members_others + 1
    
            
    # Sum up totals at the end of loop
    total_duration_of_all_answered_calls = lang_call_duration
    
    broadcastRec.total_calls_duration = total_duration_of_all_answered_calls                
    broadcastRec.total_members_tried = total_members_tried
    broadcastRec.total_members_answered = total_members_answered
    broadcastRec.total_members_dnd = total_members_dnd    
    broadcastRec.total_members_others = total_members_others    
    broadcastRec.total_members_failed = total_members_failed
    broadcastRec.total_call_units = call_units_counter        
    broadcastRec.put()

    return broadcastRec
  
  
  
def send_broadcast_complete_notification(broadcastRec):
    """" Sends Broadcast complete notification to admin"""
    #Send Notification to admin and super admin
    
    logging.debug("Sending Broadcast notification SMS..")
    total_answered = broadcastRec.total_members_answered
    total_tried = broadcastRec.total_members_tried
    total_dnd = broadcastRec.total_members_dnd
    total_failed = broadcastRec.total_members_failed
    total_amount = broadcastRec.total_amount
    balance1 = broadcastRec.parent_account.balance1
    balance2 = broadcastRec.parent_account.balance2
    
    
    smsMsg = str(broadcastRec.parent_group.name) + " Voice Broadcast completed." +  "Summary:- "  +  "Total Calls attempted: " + str(total_tried)  
    smsMsg = smsMsg +  ", Answered: " + str(total_answered) + ", DND: " + str(total_dnd) + ", Failed: " + str(total_failed) 
    smsMsg = smsMsg + ", Total Cost: " + str(total_amount) + ", Balance1: " + str(balance1) + ", Balance2: " + str(balance2)
    
    
    memberRec = broadcastRec.parent_member
    smsTo = memberRec.mobile1
    logging.debug("To: %s, Msg=%s", smsTo, smsMsg) 
    gLib.send_sms(smsTo, smsMsg)    
    
      
    
class boEmpty():
    """ An empty class that can take any properties, used as a transport mech for situations
    where data is pulled from multiple model entities but creation of a dedicated class is not 
    yet seen as required """    
    
    
    
    
    