import unittest
from application import server
from application.server import app
from application.server import build_system_of_record_json_string
from application.server import return_signed_data

import os

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        app.config.from_object(os.environ.get('SETTINGS'))
        self.app = server.app.test_client()

    def test_server(self):
        self.assertEqual((self.app.get('/')).status, '200 OK')

    def test_build_system_of_record_json_string(self):
        test_string = build_system_of_record_json_string({"a":"1"}, {"b":"2" })
        self.assertEqual('{"sig": {"b": "2"}, "data": {"a": "1"}}', test_string)

    def test_return_signed_data(self):
        signed_string = return_signed_data('{"titleno": "DN1"}')
        self.assertEqual(signed_string, "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ")

    # test sign
    # test verify
    # test insert

