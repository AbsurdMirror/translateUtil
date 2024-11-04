import nltk
from nltk.tokenize import word_tokenize, sent_tokenize  
from nltk.tag import pos_tag  
from nltk.stem import WordNetLemmatizer  
import json
import requests

f = open("CaiYunXiaoYi.token")
CaiYunXiaoYiToken = f.read()

def is_empty_or_whitespace_only(s):
    return s.strip() == ""

def nltk_update():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

def tranlateCaiYunXiaoYi(source, direction):
    url = "http://api.interpreter.caiyunai.com/v1/translator"

    # WARNING, this token is a test token for new developers,
    # and it should be replaced by your token

    payload = {
        "source": source,
        "trans_type": direction,
        "request_id": "demo",
        "detect": True,
    }

    headers = {
        "content-type": "application/json",
        "x-authorization": "token " + CaiYunXiaoYiToken,
    }

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:  
        print("Error code:", response.status_code, response.text)
    return json.loads(response.text)["target"]

def split_string_by_english_sentences(input_string):  
    # 将换行符替换为空格  
    input_string_no_newline = input_string.replace('\r', ' ')
    input_string_no_newline = input_string_no_newline.replace('\n', ' ')

    sentences = nltk.sent_tokenize(input_string_no_newline)

    return input_string_no_newline, sentences

def tranlateText(source_content):
    if is_empty_or_whitespace_only(source_content):  
        return ""
    no_newline_content, tranlate_source = split_string_by_english_sentences(source_content)
    tranlate_target = tranlateCaiYunXiaoYi(tranlate_source, "auto2zh")

    tranlate_source_target = ""
    i = 0
    for item in tranlate_source:
        tranlate_source_target += "\n===\n" + item + "\n---" + tranlate_target[i] + "\n==="
        i = i + 1

    return tranlate_source_target
