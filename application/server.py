from flask import Flask, request
from Crypto.PublicKey import RSA
from setup_logging import setup_logging
from requests.exceptions import ConnectionError
import traceback
import requests
import os
import json
import jws
from werkzeug.exceptions import HTTPException
from jws.algos import SignatureError

setup_logging()

app = Flask(__name__)
app.config.from_object(os.environ.get('SETTINGS'))

@app.route("/")
def check_status():
    app.logger.info("Everything is OK")
    return "Everything is OK"

@app.route("/sign", methods=["POST"])
def sign_title_version():
    try:
        app.logger.info("Signing title")
        title = json.dumps(request.get_json())
        signed_title = return_signed_data(title)
    except HTTPException as err:
        log_error(err, '')
        return str(err), err.code
    except MintUserException as err:
        return str(err), 500
    except Exception as err:
        unknown_error = 'unknown error signing title '
        log_error(err, unknown_error)
        return unknown_error, 500
    else:
        return str(signed_title), 200


@app.route("/verify", methods=["POST"])
def verify_title_version():
    try:
        app.logger.info("Verifying title")
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
        log_error(err, '')
        return str(err), err.code
    except SignatureError as err:
        signature_error = 'Could not validate signature'
        app.logger.info(signature_error)
        return signature_error, 200
    except MintUserException as err:
        return str(err), 500
    except Exception as err:
        unknown_error = 'unknown error in application.server.verify_title_version '
        log_error(err, unknown_error)
        return unknown_error, 500
    else:
        if the_result:
            return "verified", 200
        else:
            pass  # aws will raise a SignatureError


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

        app.logger.info("Signing title and sending it to system of record")

        response = requests.post(url, data=save_this, headers=headers)

    except HTTPException as err:
        log_error(err, '')
        return str(err), err.code
    except ConnectionError as err:
        connection_error = 'Unable to connect to system of record '
        log_error(err, connection_error)
        return connection_error, 500
    except MintUserException as err:
        return str(err), 500
    except Exception as err:
        unknown_error = 'unknown error in application.server.insert_new_title_version '
        log_error(err, unknown_error)
        return unknown_error, 500
    else:
        return response.text, 201


def return_signed_data(data):
    try:
        key = get_key()
        header = {'alg': 'RS256'}
        sig = jws.sign(header, data, key)
    except MintUserException:
        raise  # re-raise key exception, don't log again.
    except Exception as err:
        signing_failed = 'Signing failed.  Check logs.'
        log_error(err, signing_failed)
        raise MintUserException(signing_failed)
    else:
        return str(sig)


def build_system_of_record_json_string(original_data_dict, signed_data_string):
    try:
        system_of_record_dict = {"data": original_data_dict, "sig":signed_data_string}
        system_of_record_json = json.dumps(system_of_record_dict)
    except Exception as err:
        formatting_failed = 'Formatting data failed.  Check logs.'
        log_error(err, formatting_failed)
        raise MintUserException(formatting_failed)
    else:
        return system_of_record_json


def get_key(key_path='test_keys/test_private.pem'):
    try:
        key_data = open(key_path).read()
        key = RSA.importKey(key_data)
    except IOError as err:
        no_key = "Cannot find signing key. Check logs"
        log_error(err, no_key)
        raise MintUserException(no_key)
    else:
        return key


def log_error(an_error, error_message):
    #Logs an exception.  Caught exceptions will be logged with this
    #operation.  Then a new MintUserException should be raised, with a
    #Friendly message that can be displayed to the user.
    log_message = error_message + str(an_error)
    app.logger.error(log_message)
    app.logger.error(traceback.format_exc())
    return True

class MintUserException(Exception):
    pass

