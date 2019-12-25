#!/usr/bin/env python

import sys
import json
import logging
from math import exp
import requests as rq
import re

### For NLP post-processing
header={"Content-Type": "application/json"}
message='{"sample":"Hello bigdata"}'     
api_url="http://192.168.1.197:11992/norm"
###

def NLP_process_output(pre_str):
    try:        
        jmsg=json.loads(message)
        jmsg['sample']=pre_str
        r = rq.post(api_url,json=jmsg, headers=header)        
        results = json.loads(r.text)['result']
        logging.info("NLP=%s" % results)
        return results
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to get NLP post-processing: %s : %s " % (exc_type, exc_value))
        return pre_str
def post_process_json(str):
    try:
        event = json.loads(str)
        if "result" in event:
            if len(event["result"]["hypotheses"]) > 1:
                likelihood1 = event["result"]["hypotheses"][0]["likelihood"]
                likelihood2 = event["result"]["hypotheses"][1]["likelihood"]
                confidence = likelihood1 - likelihood2
                confidence = 1 - exp(-confidence)
            else:
                confidence = 1.0e+10
            event["result"]["hypotheses"][0]["confidence"] = confidence
            org_trans = event["result"]["hypotheses"][0]["transcript"]   
            logging.info("Recognized result=%s" % org_trans )         
            out_trans = NLP_process_output(org_trans) + '.'
            out_trans = 
            logging.info("Pass into funtion is %s" % out_trans)
            event["result"]["hypotheses"][0]["transcript"] = out_trans
            del event["result"]["hypotheses"][1:]
        return json.dumps(event)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to process JSON result: %s : %s " % (exc_type, exc_value))
        return str

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")

    lines = []
    while True:
        l = sys.stdin.readline()
        if not l: break # EOF
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
