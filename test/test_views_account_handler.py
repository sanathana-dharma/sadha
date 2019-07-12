import base_test
from db import models


class TestAccountListHandler(base_test.BaseTest):
  def test_get_response_ok(self):
    response = self._make_req('/main/')
    self.assertEqual(response.status_code, 200)

  def test_get_accounts_displayed_on_page(self):
    member = models.Members(name='test-member').put()
    models.Accounts(name='test-account-name',
                    account_admin_member_id=str(member.id())).put()
    response = self._make_req('/main/')
    self.assertIn('test-member', response.body)
    self.assertIn('test-account-name', response.body)
