#!/usr/bin/env python
import argparse
import sys
import json
import logging
import requests
from urllib import urlencode
from math import exp

fptai_uri = None
qna_uri = None

def post_process_json(str_event):
    try:
        event = json.loads(str_event)
        if "result" in event:
            if len(event["result"]["hypotheses"]) > 1:
                likelihood1 = event["result"]["hypotheses"][0]["likelihood"]
                likelihood2 = event["result"]["hypotheses"][1]["likelihood"]
                confidence = likelihood1 - likelihood2
                confidence = (1 - exp(-confidence)) * 100
            else:
                confidence = 100
            app_token = event.get("user_id")
            service_type = event.get("content_id")
            transcript = event["result"]["hypotheses"][0]["transcript"]
            event["result"]["hypotheses"][0]["confidence"] = confidence
	    event["result"]["hypotheses"][0]["test_app_token"] = app_token
	    event["result"]["hypotheses"][0]["test_service_type"] = service_type
            event["result"]["hypotheses"][0]["transcript"] = transcript[0].upper() + transcript[1:] + '. '
            del event["result"]["hypotheses"][1:]
        return json.dumps(event)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to process JSON result: %s : %s " % (exc_type, exc_value))
        return str_event


def get_qna(text, app_code):
    if qna_uri is None:
        return None

    try:
        headers = {'Authorization': app_code}
        query = urlencode({'text': text.encode("utf-8")})
        response = requests.request("GET", "{}?{}".format(qna_uri, query), headers=headers)
        result = json.loads(response.text)
        if len(result) == 0:
            return None
        if result[0]["source"] != "fptai":
            return None
        return result[0]
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to get qna: %s : %s " % (exc_type, exc_value))
        return None

def detect_intent(text, app_token):
    if fptai_uri is None:
        return None

    try:
        headers = {'Authorization': 'Bearer %s' % app_token}
        request_body = json.dumps(dict(content=text))

        response = requests.request("POST", fptai_uri, data=request_body, headers=headers)
        result = json.loads(response.text)
        if len(result['data']['intents']) == 0:
            return None
        return result['data']['intents'][0]
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to predict intent using FPT.AI: %s : %s " % (exc_type, exc_value))
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    parser = argparse.ArgumentParser(description='FPT.AI Integration Post Processor')
    parser.add_argument('-u', '--fptai-uri', default="https://api.fpt.ai/v2/predict", dest="fptai_uri")
    parser.add_argument('-q', '--qna-uri', default="https://qna.fpt.ai/api/bot/findanswer", dest="qna_uri")
    args = parser.parse_args()
    if args.fptai_uri:
        fptai_uri = args.fptai_uri
    if args.qna_uri:
        qna_uri = args.qna_uri
    lines = []
    while True:
        l = sys.stdin.readline()
        if not l: break  # EOF
        if l.strip() == "":
            if len(lines) > 0:
                result_json = post_process_json("".join(lines))
                print result_json
                print
                sys.stdout.flush()
                lines = []
        else:
            lines.append(l)

    if len(lines) > 0:
        result_json = post_process_json("".join(lines))
        print result_json
        lines = []
