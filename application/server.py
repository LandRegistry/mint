from flask import Flask, request
from application import app
from Crypto.PublicKey import RSA
from requests.exceptions import ConnectionError
import traceback
import requests
import os
import json
import jws
from werkzeug.exceptions import HTTPException
from jws.algos import SignatureError
from python_logging.setup_logging import setup_logging
from python_logging.logging_utils import linux_user, client_ip, log_dir

INFO_LOG_FILENAME='debug'
ERROR_LOG_FILENAME='error'


@app.route("/")
def check_status():
    app.logger.info("Everything is OK")
    return "Everything is OK"

@app.route("/sign", methods=["POST"])
def sign_title_version():
    try:
        title = json.dumps(request.get_json())
        signed_title = return_signed_data(title)
    except HTTPException as err:
        http_exception = '. HTTP exception occurred. '
        app.logger.error(http_exception)
        app.logger.error(traceback.format_exc())
        return http_exception, err.code
    except MintUserException as err:
        app.logger.error(make_log_msg(str(err), request, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return str(err), 500
    except Exception as err:
        unknown_error = '. unknown error signing title. '
        app.logger.error(make_log_msg(unknown_error, request, ERROR_LOG_FILENAME, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return unknown_error, 500
    else:
        app.logger.info(
            make_log_msg(". AUDIT: Completed signing title. ", request, INFO_LOG_FILENAME, get_title_number(request)))
        return str(signed_title), 200


@app.route("/verify", methods=["POST"])
def verify_title_version():
    try:
        signed_title = request.get_json()
        signature = signed_title['sig']

        #signed_data is currently unicode.  Incompatible with JWS.  Convert to ASCII
        signature = signature.encode('ascii', 'ignore')
        title = json.dumps(signed_title['data'])

        # #import keys
        key = get_key()
        header = {'alg': 'RS256'}
        the_result = jws.verify(header, title, signature, key)

    except HTTPException as err:
        http_exception = '. HTTP exception occurred. '
        app.logger.error(http_exception)
        app.logger.error(traceback.format_exc())
        return http_exception, err.code
    except SignatureError as err:
        signature_error = '. Could not validate signature. '
        app.logger.info(signature_error)
        return signature_error, 200
    except MintUserException as err:
        app.logger.error(make_log_msg(str(err), request, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return str(err), 500
    except Exception as err:
        unknown_error = '. unknown error in application.server.verify_title_version. '
        app.logger.error(make_log_msg(unknown_error, request, ERROR_LOG_FILENAME, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return unknown_error, 500
    else:
        if the_result:
            app.logger.info(
                make_log_msg(". AUDIT: Verified signed title. ", request, INFO_LOG_FILENAME, get_title_number(request)))
            return "verified", 200
        #otherwise aws will raise a SignatureError


@app.route("/insert", methods=["POST"])
def insert_new_title_version():
    try:
        data_dict = request.get_json()
        data = json.dumps(data_dict)
        signed_data = return_signed_data(data)
        save_this = build_system_of_record_json_string(data_dict, signed_data)

        server = app.config['SYSTEM_OF_RECORD']
        route = '/insert'
        url = server + route

        headers = {'Content-Type': 'application/json'}

        app.logger.info(
            make_log_msg(". AUDIT: Signed title and sending to system of record. ", request, INFO_LOG_FILENAME,
                         get_title_number(request)))

        response = requests.post(url, data=save_this, headers=headers)

    except HTTPException as err:
        http_exception = '.HTTP exception occurred. '
        app.logger.error(http_exception)
        app.logger.error(traceback.format_exc())
        return http_exception, err.code
    except ConnectionError as err:
        connection_error = '. Unable to connect to system of record. '
        app.logger.error(make_log_msg(connection_error, request, ERROR_LOG_FILENAME, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return connection_error, 500
    except MintUserException as err:
        app.logger.error(make_log_msg(str(err), request, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return str(err), 500
    except Exception as err:
        unknown_error = '. unknown error in application.server.insert_new_title_version. '
        app.logger.error(make_log_msg(unknown_error, request, ERROR_LOG_FILENAME, get_title_number(request)))
        app.logger.error(traceback.format_exc())
        return unknown_error, 500
    else:
        app.logger.info(
            make_log_msg(". AUDIT: System of record responded with: %s, status code: %s. " % (
                response.text, response.status_code), request, INFO_LOG_FILENAME, get_title_number(request)))
        return response.text, response.status_code


def return_signed_data(data):
    try:
        key = get_key()
        header = {'alg': 'RS256'}
        sig = jws.sign(header, data, key)
    except MintUserException:
        raise  # re-raise key exception, don't log again.
    except Exception as err:
        signing_failed = '. Signing failed.  Check logs. '
        raise MintUserException(signing_failed)
    else:
        return str(sig)


def build_system_of_record_json_string(original_data_dict, signed_data_string):
    try:
        system_of_record_dict = {"data": original_data_dict, "sig":signed_data_string}
        system_of_record_json = json.dumps(system_of_record_dict)
    except Exception as err:
        formatting_failed = '. Formatting data failed.  Check logs. '
        raise MintUserException(formatting_failed)
    else:
        return system_of_record_json


def get_key(key_path='test_keys/test_private.pem'):
    try:
        key_data = open(key_path).read()
        key = RSA.importKey(key_data)
    except IOError as err:
        no_key = ". Cannot find signing key. Check logs. "
        raise MintUserException(no_key)
    else:
        return key


class MintUserException(Exception):
    pass


def make_log_msg(message, request, log_level, title_number):
    #Constructs the message to submit to audit.
    msg = message + 'Client ip address is: %s. ' % client_ip(request)
    msg = msg + 'Signed in as: %s. ' % linux_user()
    msg = msg + 'Title number is: %s. ' % title_number
    msg = msg + 'Logged at: mint/%s. ' % log_dir(log_level)
    return msg


def get_title_number(request):
    #gets the title number from minted json
    try:
        if 'data' not in request.get_json():
            return request.get_json()['title_number']
        else:
            return request.get_json()['data']['title_number']

    except Exception as err:
        error_message = ". title number not found. Check JSON format: "
        app.logger.error(make_log_msg(error_message, request, ERROR_LOG_FILENAME, request.get_json()))
        return error_message + str(err)