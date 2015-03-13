import unittest
from application import server
from application.server import app
from application.server import build_system_of_record_json_string
from application.server import return_signed_data
from application.server import MintUserException
from application.server import get_key
from application.server import log_error
import os

import mock

TEST_TITLE = '{"titleno": "DN1"}'
BAD_JSON = {"bad_json"}
TEST_SIGNATURE = "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ"
VERIFY_DATA = '{"sig" : "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ", "data":{"titleno" : "DN1"}}'
#VERIFY_DATA_FAIL refers to titleno DN2,  to verify the title_no needs to be DN1
VERIFY_AMENDED_DATA = '{"sig" : "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ", "data":{"titleno" : "DN2"}}'
#Removed the first character of the key
VERIFY_DATA_AMENDED_KEY = '{"sig" : "6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ", "data":{"titleno" : "DN1"}}'

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = server.app.test_client()

    def test_server(self):
        self.assertEqual((self.app.get('/')).status, '200 OK')

    def test_build_system_of_record_json_string(self):
        test_string = build_system_of_record_json_string({"a":"1"}, {"b":"2" })
        self.assertEqual('{"sig": {"b": "2"}, "data": {"a": "1"}}', test_string)

    def test_build_system_of_record_json_string_exception(self):
        self.assertRaises(MintUserException, build_system_of_record_json_string, BAD_JSON, BAD_JSON )

    def test_build_system_of_record_json_string_exception_message(self):
        with self.assertRaises(MintUserException) as context:
            build_system_of_record_json_string(BAD_JSON, BAD_JSON)
        self.assertTrue('Formatting data failed.  Check logs.' in context.exception)

    def test_return_signed_data(self):
        signed_string = return_signed_data(TEST_TITLE)
        self.assertEqual(signed_string, TEST_SIGNATURE)

    def test_return_signed_data_exception(self):
        self.assertRaises(MintUserException, return_signed_data, BAD_JSON)

    def test_return_signed_data_exception_message(self):
        with self.assertRaises(MintUserException) as context:
            return_signed_data(BAD_JSON)
        self.assertTrue('Signing failed.  Check logs.' in context.exception)

    def test_get_key(self):
        self.assertTrue(get_key() is not None)

    def test_get_key_exception(self):
        self.assertRaises(MintUserException, get_key, 'bad file path')

    def test_get_key_exception_message(self):
        with self.assertRaises(MintUserException) as context:
            return get_key('bad file path')
        self.assertTrue('Cannot find signing key. Check logs' in context.exception)

    def test_logs_error(self):
        #Force an error and check it logs
        with self.assertRaises(MintUserException) as context:
            return get_key('bad file path')
        # log_errors returns true
        self.assertTrue(log_error(context.exception, 'test message'))


    def test_sign_route(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/sign', data = TEST_TITLE, headers = headers)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.data, TEST_SIGNATURE)

    def test_sign_route_400(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/sign', data='', headers=headers)
        self.assertEqual(response.status, '400 BAD REQUEST')

    def test_verify_route(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data = VERIFY_DATA, headers = headers)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.data, "verified")

    def test_verify_route_cannot_verify(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data=VERIFY_AMENDED_DATA, headers=headers)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.data, "Could not validate signature")

    def test_verify_route_unknown_exception(self):
    #An incorrect key causes an unknown exception.  If the key is invalid
    #Then a generic TypeError is returned - which is too vague to handle.
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data=VERIFY_DATA_AMENDED_KEY, headers=headers)
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')
        self.assertTrue("unknown error in application.server.verify_title_version" in response.data)

    def test_verify_route_400(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data='', headers=headers)
        self.assertEqual(response.status, '400 BAD REQUEST')

    @mock.patch('requests.post')
    @mock.patch('requests.Response')
    def test_insert_route(self, mock_response, mock_post):
        mock_response.text = "row inserted"
        mock_post.return_value = mock_response
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, "row inserted")

    def test_insert_route_400(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data='', headers=headers)
        self.assertEqual(response.status, '400 BAD REQUEST')

