import mock
import base_test
from db import models
from core import ivrapi


class TestCallAPI(base_test.BaseTest):
  api = ivrapi.CallApi(host='')

  def test_check_dnd(self):
    with mock.patch('google.appengine.api.urlfetch.fetch') as fetch:
      type(fetch.return_value).content = mock.PropertyMock(
        return_value='<response><status>success</status><message>DND'
                     '</message></response>')
      self.assertEqual(self.api.check_dnd(123), 'DND')

  def test_update_calllog(self):
    callog = self.api.update_calllog(
      cid='3',
      to_mobile='123',
      from_mobile='321',
      api='twilio',
      num_type='DND',
      member_id='1',
      member_name='john',
      broadcast_id='2')
    entity = callog.key.get()
    self.assertEqual(entity.status, 'queued')
    self.assertEqual(entity.cid, '3')

  def test_place_call_non_dnd(self):
    with mock.patch('core.ivrapi.KookooCall.call') as koookooo:
      koookooo.return_value = '576'
      with mock.patch('core.ivrapi.CallApi.update_calllog') as update_callog:
        with mock.patch('core.ivrapi.CallApi.check_dnd') as check_dnd:
          check_dnd.return_value = 'NON-DND'
          self.api.place_call(
            to_mobile='123',
            from_mobile='321',
            member_id='1',
            member_name='john',
            broadcast_id='2'
          )
          update_callog.assert_called_once_with(
            '576', '123', '918049202255', 'kookoo', 'Regular', '1', 'john', '2')

  def test_place_call_non_dnd_starts_with_max_task_created(self):
    with mock.patch('core.ivrapi.KookooCall.call') as koookooo:
      koookooo.return_value = 'Max576'
      with mock.patch('core.ivrapi.CallApi.check_dnd') as check_dnd:
        check_dnd.return_value = 'NON-DND'
        self.api.place_call(
          to_mobile='123',
          from_mobile='321',
          member_id='1',
          member_name='john',
          broadcast_id='2'
        )
        self.assertEqual(self.tasks_in_queue('default'), 1)

  def test_place_call_dnd(self):
    with mock.patch('core.ivrapi.TwilioCall.call') as twilio:
      twilio.return_value = '576'
      with mock.patch('core.ivrapi.CallApi.update_calllog') as update_callog:
        with mock.patch('core.ivrapi.CallApi.check_dnd') as check_dnd:
          check_dnd.return_value = 'DND'
          self.api.place_call(
            to_mobile='123',
            from_mobile='321',
            member_id='1',
            member_name='john',
            broadcast_id='2'
          )
          update_callog.assert_called_once_with(
            '576', '123', '+918049202255', 'twilio', 'DND', '1', 'john', '2')


class TestKookooCall(base_test.BaseTest):
  api = ivrapi.KookooCall()

  def test_call(self):
    with mock.patch('google.appengine.api.urlfetch.fetch') as fetch:
      type(fetch.return_value).content = mock.PropertyMock(
        return_value='<response><status>success</status><message>BLA'
                     '</message></response>')
      message = self.api.call(
        to_mobile='123',
        voice_url='voice',
        callback_url='callback',
      )
      fetch.assert_called_once_with(
        url='http://www.kookoo.in/outbound/outbound.php?api_key=KKd1a4f4f7443412a34841727bff2514df&outbound_version=2&url=voice,kookoo&phone_no=0123&caller_id=918049202255&callback_url=callback?api=kookoo',
        deadline=60)
      self.assertEqual(message, 'BLA')


class TestTwilioCall(base_test.BaseTest):
  api = ivrapi.TwilioCall()

  def test_call(self):
    with mock.patch('core.ivrapi.TwilioRestClient') as TwilioRestClient:
      sid = self.api.call(
        to_mobile='123',
        from_mobile='321',
        voice_url='voice',
        callback_url='callback',
      )
      TwilioRestClient.assert_called_once_with(
        'AC997b96a30773db043a91948953629a45', '48a9b7725a7c59301176821a155d06c0')
