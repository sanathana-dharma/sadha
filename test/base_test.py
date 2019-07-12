import unittest
import pickle
import logging
import urllib
import os

from google.appengine.ext import ndb, testbed, deferred
import webapp2

import appengine_config
import web

appengine_config.DEV_SERVER = True
appengine_config.DEBUG = True
# Turn off the noisy debug logs from NDB
ndb.utils.DEBUG = False


class BaseTest(unittest.TestCase):
  nosegae_app_identity_service = True
  nosegae_blobstore = True
  nosegae_urlfetch = True
  nosegae_datastore_v3 = True
  nosegae_taskqueue = True
  nosegae_user = True
  nosegae_mail = True

  uid = None
  req = webapp2.Request.blank('/')
  req.app = web.application

  def _webapp_set_globals(self):
    web.application.set_globals(app=web.application, request=self.req)

  def setUp(self):
    self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
    self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
    os.environ['DEFAULT_VERSION_HOSTNAME'] = 'localhost:8080'

  def _make_req(self, _name, *args, **kwargs):
    """Get response by URI name
    Use a dummy request just to be able to use uri_for()

    Args:
      _name: URI to make request on.
      _method: HTTP method to use with request.
      _payload: Dictionary with payload append to request.
      _headers: Dictionary with headers append to request.

    Returns:
      webapp2.Response object.
    """
    self._webapp_set_globals()

    _payload = kwargs.pop('_payload', None)
    if _payload is not None and isinstance(_payload, dict):
      _payload = urllib.urlencode(_payload)

    params = {'method': kwargs.pop('_method', 'GET'),
              'POST': _payload,
              'headers': kwargs.pop('_headers', {})}

    res = web.application.get_response(_name, **params)
    return res

  def uri(self, name, *args, **kwargs):
    self._webapp_set_globals()
    return webapp2.uri_for(name, *args, **kwargs)

  def process_queues(self, include=None, exclude=None):
    """Process all tasks in queue.

    Args:
      include: Optional list of queues to process. Default: all.
      exclude: Optional list of queues to exclude from being processed.
        If there is overlap between include and exclude, then exclude "wins."
    """
    if include is None:
      include = [q for q in self.taskqueue_stub.GetQueues()]
      include = [q['name'] for q in include if q['tasks_in_queue']]
    if exclude is None:
      exclude = []

    include = [q for q in include if q not in exclude]

    for queue in include:
      tasks = self.taskqueue_stub.GetTasks(queue)
      while tasks:
        self.taskqueue_stub.FlushQueue(queue)
        for task in tasks:
          logging.debug('Executing task %s on %s', task['name'], task['url'])
          if task['url'].startswith(deferred.deferred._DEFAULT_URL):
            (func, args, opts) = pickle.loads(task['body'].decode('base64'))
            func(*args)
          else:
            payload = task['body'].decode('base64')
            res = self._make_req(task['url'], _headers=dict(task['headers']),
                                 _payload=payload, _relative=True,
                                 _method=task['method'])
            if res.status_code not in range(200, 299):
              raise deferred.PermanentTaskFailure(task)
        tasks = self.taskqueue_stub.GetTasks(queue)

  def tasks_in_queue(self, queue):
    """Return the number of tasks in the given queue;

    Args:
      queue: String with queue name.
    """
    return len(self.taskqueue_stub.GetTasks(queue))
