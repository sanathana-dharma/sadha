import base_test
from db import models


class TestMembers(base_test.BaseTest):

  def test_add_member(self):
    models.Members.add_member(name='test', city='NY')
    member = models.Members.query().get()
    self.assertEqual(member.name, 'test')
    self.assertEqual(member.city, 'NY')

  def test_get_member(self):
    key = models.Members(name='test').put()
    self.assertEqual(models.Members.get_member(key.id()).name, 'test')

  def test_search_by_name_mobile(self):
    pass

  def test_update_member(self):
    key = models.Members(name='john').put()
    models.Members.update_member(
      member_id=key.id(), name='david', mobile_numbers='123',
      date_of_birth='april', gender='male')
    self.assertEqual(key.get().name, 'david')


class TestCallLogs(base_test.BaseTest):

  def test_get_error_logs(self):
    models.CallLogs(mobile_number='123', status='error').put()
    self.assertEqual(len(models.CallLogs.get_error_logs()), 1)

  def test_get_error_logs_not_returned_for_non_error(self):
    models.CallLogs(mobile_number='123', status='ok').put()
    self.assertEqual(len(models.CallLogs.get_error_logs()), 0)
