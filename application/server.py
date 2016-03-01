from flask import Flask, request
from application import app
from Crypto.PublicKey import RSA
from requests.exceptions import ConnectionError
import traceback
import requests
import os
import pwd
import json
import jws
from werkzeug.exceptions import HTTPException
from jws.algos import SignatureError
import datetime
import logging
import sys
import pwd


logging.basicConfig(format='%(levelname)s %(asctime)s [Mint] Message: %(message)s', level=logging.INFO, datefmt='%d.%m.%y %I:%M:%S %p')


@app.route("/")
def check_status():
    logging.info("Mint status check OK")
    return "Everything is OK"

@app.route("/sign", methods=["POST"])
def sign_title_version():
    try:
        title = json.dumps(request.get_json())
        signed_title = return_signed_data(title)
    except HTTPException as err:
        logging.error('HTTP exception occurred.')
        logging.error( traceback.format_exc() )
        return 'HTTP exception occurred.', err.code
    except MintUserException as err:
        logging.error( make_log_msg( str(err), get_title_number(request) ) )
        logging.error( traceback.format_exc )
        return str(err), 500
    except Exception as err:
        logging.error( make_log_msg( 'Unknown error signing title.', get_title_number(request) ) )
        logging.error( traceback.format_exc )
        return 'Unknown error signing title.', 500
    else:
        logging.info( make_log_msg( 'Completed signing title.', get_title_number(request) ) )
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
        logging.error('HTTP exception occurred.')
        logging.error( traceback.format_exc() )
        return 'HTTP exception occurred.', err.code
    except SignatureError as err:
        logging.error('Could not validate signature.')
        return 'Could not validate signature.', 200
    except MintUserException as err:
        logging.error( make_log_msg( str(err), get_title_number(request) ) )
        logging.error( traceback.format_exc )
        return str(err), 500
    except Exception as err:
        logging.error( make_log_msg( 'Unknown error in application.server.verify_title_version.', get_title_number(request) ) )
        logging.error( traceback.format_exc )
        return 'Unknown error in application.server.verify_title_version.', 500
    else:
        if the_result:
            logging.info( make_log_msg( 'Verified signed title.', get_title_number(request) ) )
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

        logging.info( make_log_msg( 'Signed and sending to system of record.', get_title_number(request) ) )

        response = requests.post(url, data=save_this, headers=headers)

    except HTTPException as err:
        logging.error('HTTP exception occurred.')
        logging.error( traceback.format_exc() )
        return 'HTTP exception occurred.', err.code
    except ConnectionError as err:
        logging.error('Unable to connect to system of record.')
        logging.error( traceback.format_exc() )
        return 'Unable to connect to system of record.', 500
    except MintUserException as err:
        logging.error( make_log_msg( str(err), get_title_number(request) ) )
        logging.error( traceback.format_exc )
        return str(err), 500
    except Exception as err:
        logging.error( make_log_msg( 'Unknown error in application.server.insert_new_title_version.', get_title_number(request) ) )
        logging.error( traceback.format_exc )
        return 'Unknown error in application.server.insert_new_title_version.', 500
    else:
        logging.info( make_log_msg( "{}Status Code: {}".format(response.text, response.status_code), get_title_number(request) ) )
        return response.text, response.status_code


def return_signed_data(data):
    try:
        key = get_key()
        header = {'alg': 'RS256'}
        sig = jws.sign(header, data, key)
    except MintUserException:
        raise  # re-raise key exception, don't log again.
    except Exception as err:
        signing_failed = 'Signing failed.  Check logs.'
        raise MintUserException(signing_failed)
    else:
        return str(sig)


def build_system_of_record_json_string(original_data_dict, signed_data_string):
    try:
        system_of_record_dict = {"data": original_data_dict, "sig":signed_data_string}
        system_of_record_json = json.dumps(system_of_record_dict)
    except Exception as err:
        formatting_failed = 'Formatting data failed.  Check logs.'
        raise MintUserException(formatting_failed)
    else:
        return system_of_record_json


def get_key(key_path='test_keys/test_private.pem'):
    try:
        key_data = open(key_path).read()
        key = RSA.importKey(key_data)
    except IOError as err:
        no_key = 'Cannot find signing key. Check logs.'
        raise MintUserException(no_key)
    else:
        return key


class MintUserException(Exception):
    pass


def make_log_msg(message, title_number=''):
    #     if app.config['ENABLE_AUTH'] is False:
    #     return 'Raised by: test, Message: ' + message
    # else:
    if title_number == '':
        return 'Raised by: ' + linux_user() + ', Message: ' + message
    else:
        return 'Raised by: ' + linux_user() + ', Title Number: ' + title_number + ', Message: ' + message


def linux_user():
    try:
        return pwd.getpwuid(os.geteuid()).pw_name
    except Exception as err:
        return "failed to get user: %s" % err


def get_title_number(request):
    #gets the title number from minted json
    try:
        if 'data' not in request.get_json():
            return request.get_json()['title_number']
        else:
            return request.get_json()['data']['title_number']

    except Exception as err:
        logging.error( 'Title number not found. Check JSON format:', request.get_json() )
        return error_message + str(err)