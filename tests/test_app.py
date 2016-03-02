from flask import request
import unittest
from application import server
from application.server import app
from application.server import build_system_of_record_json_string
from application.server import return_signed_data
from application.server import MintUserException
from application.server import get_title_number
from application.server import get_key
from application.server import make_log_msg
import os
import time
import mock
from requests.exceptions import ConnectionError

TEST_TITLE = '{"title_number": "DN1"}'
BAD_JSON = {"bad_json"}
TEST_SIGNATURE = "xGM837iKCZDNUX2031XlPDKLsQ8y6uFs2_1DXqjATUjkAbWS5WFq2hR6MnWDgXC95rjg8h5lmKSUV-8c0W8WSaVaRfjEBz5vFOY3HtU0gXggXSYfLlKoEYT-c4BfySVwxWk1wSuE1F3tHJshJ4Dzx85brJJ6UePE2ZG8oczbBEQxhh09MDtaskNbtmpN8Pd43Ct7SJhHJqHbNT812mZjmoMqp9WJln0N0MDSh0_2Oc-cttJkIToW2AvniiTeK9TMEXo7xRPdkObYuG8gYEWlyKT981gnFz3TgKJJyMjQZTmrUCzcEEb4pMzKoc9jqiivJLD900KgoiC8MtcgNX7Kmw"
VERIFY_DATA = '{"sig" : "xGM837iKCZDNUX2031XlPDKLsQ8y6uFs2_1DXqjATUjkAbWS5WFq2hR6MnWDgXC95rjg8h5lmKSUV-8c0W8WSaVaRfjEBz5vFOY3HtU0gXggXSYfLlKoEYT-c4BfySVwxWk1wSuE1F3tHJshJ4Dzx85brJJ6UePE2ZG8oczbBEQxhh09MDtaskNbtmpN8Pd43Ct7SJhHJqHbNT812mZjmoMqp9WJln0N0MDSh0_2Oc-cttJkIToW2AvniiTeK9TMEXo7xRPdkObYuG8gYEWlyKT981gnFz3TgKJJyMjQZTmrUCzcEEb4pMzKoc9jqiivJLD900KgoiC8MtcgNX7Kmw", "data":{"title_number": "DN1"}}'
#VERIFY_DATA_FAIL refers to titleno DN2,  to verify the title_no needs to be DN1
VERIFY_AMENDED_DATA = '{"sig" : "xGM837iKCZDNUX2031XlPDKLsQ8y6uFs2_1DXqjATUjkAbWS5WFq2hR6MnWDgXC95rjg8h5lmKSUV-8c0W8WSaVaRfjEBz5vFOY3HtU0gXggXSYfLlKoEYT-c4BfySVwxWk1wSuE1F3tHJshJ4Dzx85brJJ6UePE2ZG8oczbBEQxhh09MDtaskNbtmpN8Pd43Ct7SJhHJqHbNT812mZjmoMqp9WJln0N0MDSh0_2Oc-cttJkIToW2AvniiTeK9TMEXo7xRPdkObYuG8gYEWlyKT981gnFz3TgKJJyMjQZTmrUCzcEEb4pMzKoc9jqiivJLD900KgoiC8MtcgNX7Kmw", "data":{"title_number": "DN2"}}'
#Removed the first character of the key
VERIFY_DATA_AMENDED_KEY = '{"sig" : "GM837iKCZDNUX2031XlPDKLsQ8y6uFs2_1DXqjATUjkAbWS5WFq2hR6MnWDgXC95rjg8h5lmKSUV-8c0W8WSaVaRfjEBz5vFOY3HtU0gXggXSYfLlKoEYT-c4BfySVwxWk1wSuE1F3tHJshJ4Dzx85brJJ6UePE2ZG8oczbBEQxhh09MDtaskNbtmpN8Pd43Ct7SJhHJqHbNT812mZjmoMqp9WJln0N0MDSh0_2Oc-cttJkIToW2AvniiTeK9TMEXo7xRPdkObYuG8gYEWlyKT981gnFz3TgKJJyMjQZTmrUCzcEEb4pMzKoc9jqiivJLD900KgoiC8MtcgNX7Kmw", "data":{"title_number": "DN1"}}'
MINT_EXCEPTION_MESSAGE = 'bang!'

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
        self.assertTrue('Formatting data failed.  Check logs' in context.exception)

    def test_return_signed_data(self):
        signed_string = return_signed_data(TEST_TITLE)
        self.assertEqual(signed_string, TEST_SIGNATURE)

    def test_return_signed_data_exception(self):
        self.assertRaises(MintUserException, return_signed_data, BAD_JSON)

    def test_return_signed_data_exception_message(self):
        with self.assertRaises(MintUserException) as context:
            return_signed_data(BAD_JSON)
        self.assertTrue('Signing failed.  Check logs' in context.exception)

    @mock.patch('application.server.get_key')
    def test_returned_signed_data_reraised_mint_user_exception(self, mock_return):
        mock_return.side_effect = self.create_mint_exception
        with self.assertRaises(MintUserException) as context:
            return_signed_data(VERIFY_DATA)
        self.assertTrue(MINT_EXCEPTION_MESSAGE in context.exception)

    def test_get_key(self):
        self.assertTrue(get_key() is not None)

    def test_get_key_exception(self):
        self.assertRaises(MintUserException, get_key, 'bad file path')

    def test_get_key_exception_message(self):
        with self.assertRaises(MintUserException) as context:
            return get_key('bad file path')
        self.assertTrue('Cannot find signing key. Check logs' in context.exception)


    def test_sign_route(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/sign', data = TEST_TITLE, headers = headers)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.data, TEST_SIGNATURE)

    def test_sign_route_400(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/sign', data='', headers=headers)
        self.assertEqual(response.status, '400 BAD REQUEST')

    @mock.patch('application.server.return_signed_data')
    @mock.patch('application.server.make_log_msg')
    def test_sign_route_mint_user_exception(self, mock_make_msg, mock_return):
        mock_return.side_effect = self.create_mint_exception
        mock_make_msg.side_effect = 'z'
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/sign', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, MINT_EXCEPTION_MESSAGE)
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')

    @mock.patch('application.server.return_signed_data')
    @mock.patch('application.server.make_log_msg')
    def test_sign_route_exception(self, mock_make_msg, mock_return):
        mock_return.side_effect = self.create_exception
        mock_make_msg.side_effect = 'z'
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/sign', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, 'Unknown error signing title')
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')


    def test_verify_route(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data = VERIFY_DATA, headers=headers)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.data, "verified")

    def test_verify_route_cannot_verify(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data=VERIFY_AMENDED_DATA, headers=headers)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.data, "Could not validate signature")

    @mock.patch('requests.post')
    @mock.patch('requests.Response')
    def test_insert_route(self, mock_response, mock_post):
        mock_response.text = "row inserted"
        mock_post.return_value = mock_response
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, "row inserted")

    def test_verify_route_unknown_exception(self):
    #An incorrect key causes an unknown exception.  If the key is invalid
    #Then a generic TypeError is returned - which is too vague to handle.
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data=VERIFY_DATA_AMENDED_KEY, headers=headers)
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')
        self.assertTrue("Unknown error in application.server.verify_title_version" in response.data)

    def test_verify_route_400(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data='', headers=headers)
        self.assertEqual(response.status, '400 BAD REQUEST')

    def test_insert_route_400(self):
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data='', headers=headers)
        self.assertEqual(response.status, '400 BAD REQUEST')

    @mock.patch('application.server.get_key')
    @mock.patch('application.server.make_log_msg')
    def test_verify_route_mint_user_exception(self, mock_make_msg, mock_return):
        mock_return.side_effect = self.create_mint_exception
        mock_make_msg.side_effect = 'z'
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/verify', data=VERIFY_DATA, headers=headers)
        self.assertEqual(response.data, MINT_EXCEPTION_MESSAGE)
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')

    @mock.patch('application.server.return_signed_data')
    @mock.patch('application.server.make_log_msg')
    def test_insert_route_mint_user_exception(self, mock_make_msg, mock_return):
        mock_return.side_effect = self.create_mint_exception
        mock_make_msg.side_effect = 'z'
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, MINT_EXCEPTION_MESSAGE)
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')

    @mock.patch('application.server.return_signed_data')
    @mock.patch('application.server.make_log_msg')
    def test_insert_route_exception(self, mock_make_msg, mock_return):
        mock_return.side_effect = self.create_exception
        mock_make_msg.side_effect = 'z'
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, 'Unknown error in application.server.insert_new_title_version')
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')

    @mock.patch('application.server.return_signed_data')
    @mock.patch('application.server.make_log_msg')
    def test_insert_route_connection_exception(self, mock_make_msg, mock_return):
        mock_return.side_effect = self.create_connection_exception
        mock_make_msg.side_effect = 'z'
        headers = {'content-Type': 'application/json'}
        response = self.app.post('/insert', data=TEST_TITLE, headers=headers)
        self.assertEqual(response.data, 'Unable to connect to system of record')
        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')

    def create_mint_exception(self, *args):
        raise MintUserException(MINT_EXCEPTION_MESSAGE)

    def create_exception(self):
        raise Exception('boom!')

    def create_connection_exception(self, *args):
        raise ConnectionError('boom!')

    def test_make_log_msg(self):
        self.assertEqual(make_log_msg( 'Test Message' ), 'Test Message, Raised by: vagrant' )

    def test_get_title_number_no_title(self):
        self.assertEqual(get_title_number( {'test':'DN1'} ), 'Title number not found. Check JSON format' )

    def test_get_title_number_title_only(self):
        self.assertEqual(get_title_number( {'title_number':'DN1'} ), ( 'DN1', 'N/A', 'N/A' ) )

    def test_get_title_number_title_and_abr(self):
        self.assertEqual(get_title_number( {'title_number':'DN1', 'application_reference':'ABR1'} ), ( 'DN1', 'ABR1', 'N/A' ) )

    def test_get_title_number_title_and_abr_and_gabr(self):
        self.assertEqual(get_title_number( {'title_number':'DN1', 'application_reference':'ABR1', 'geometry_application_reference':'GABR1'} ), ( 'DN1', 'ABR1', 'GABR1' ) )

    def test_get_title_number_data_no_title(self):
        self.assertEqual(get_title_number( {'data':{'test':'DN1'}} ), 'Title number not found. Check JSON format' )

    def test_get_title_number_data_title_only(self):
        self.assertEqual(get_title_number( {'data':{'title_number':'DN1'}} ), ( 'DN1', 'N/A', 'N/A' ) )

    def test_get_title_number_data_title_and_abr(self):
        self.assertEqual(get_title_number( {'data':{'title_number':'DN1', 'application_reference':'ABR1'}} ), ( 'DN1', 'ABR1', 'N/A' ) )

    def test_get_title_number_data_title_and_abr_and_gabr(self):
        self.assertEqual(get_title_number( {'data':{'title_number':'DN1', 'application_reference':'ABR1', 'geometry_application_reference':'GABR1'}} ), ( 'DN1', 'ABR1', 'GABR1' ) )