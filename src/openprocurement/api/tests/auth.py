# -*- coding: utf-8 -*-
import os
import unittest
from pyramid import testing
from openprocurement.api.auth import AuthenticationPolicy
from pyramid.tests.test_authentication import TestBasicAuthAuthenticationPolicy


class AuthTest(TestBasicAuthAuthenticationPolicy):
    def _makeOne(self, check):
        auth_file_path = "{}/auth.ini".format(os.path.dirname(os.path.abspath(__file__)))
        return AuthenticationPolicy(auth_file_path, 'SomeRealm')

    test_authenticated_userid_utf8 = None
    test_authenticated_userid_latin1 = None

    def test_unauthenticated_userid_bearer(self):
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'Bearer chrisr'
        policy = self._makeOne(None)
        self.assertEqual(policy.unauthenticated_userid(request), 'chrisr')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
