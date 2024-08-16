import re
import sys
import requests
import json
import xmltodict
import pprint
from datetime import datetime
import pandas as pd

###############
# READ CONFIG #
###############

with open ("config.json", "r") as file:
    CFG_FILE = json.load(file)
    
###############################
# DECLARE NECESSARY FUNCTIONS #
###############################

def join_search_queries(queries_list):
    if None in queries_list:
        sys.exit("INVALID QUERY IN CONFIG FILE")
    else:
        return " or ".join(queries_list)
    
def exit_program_on_success():
    print("Exiting the program...")
    sys.exit(0)

def exit_program_on_fail(error):
    print(f"An error has occured: {error}")
    sys.exit(1)
    
def convert_xml_to_json(input_content:str) -> dict:
    data_dict = xmltodict.parse(input_content)
    data_parsed_str = json.dumps(data_dict)
    data_json = json.loads(data_parsed_str)
    return data_json

def build_data_search_q_param(headers_dict:dict) -> str:
    if len(headers_dict) == 0:
        return None
    else:
        headers_as_list = []
        for key, value in headers_dict.items():
            if key == "pd" and isinstance(value, list):
                temp = ",".join(value)
                headers_as_list.append(f'{key} within "{temp}"')
            elif key == "binding_operator":
                bind_operator = value
            elif isinstance(value, str):
                headers_as_list.append(f"{key}={value}")
        return f" {bind_operator} ".join(headers_as_list)
    
def gen_api_full_txt_url(patent_id:str, out_format:str) -> str:
    return f"{EPO_API_BASE_URL}/{EPO_API_VER}/{EPO_API_PUB_DATA}/{EPO_API_ENDPOINT_PUB}/{out_format}/{patent_id}/{EPO_API_SERVICE_FT}"

def conv_date_to_sql_comp(input_str) -> str:
    if len(input_str) == 8 and input_str.isdigit():
        year = input_str[:4]
        month = input_str[4:6]
        day = input_str[6:]
        return year + "-" + month + "-" + day
    else:
        return DATA_FORMAT_ERROR_FLAG
    
def fulltxt_avail_flg(single_patent_id:str, reponse_format:str, my_headers:dict) -> list:
    full_txt_verd=requests.get(
            url=gen_api_full_txt_url(patent_id=single_patent_id, out_format=reponse_format), 
            headers=my_headers
        )
    if full_txt_verd.status_code == 200:
        return "Y"
    else:
        return "N"
    
#####################
# DECLARE VARIABLES #
#####################

EPO_API_BASE_URL="https://ops.epo.org"
EPO_API_VER="3.2"

EPO_API_TOKEN_URL_SUFIX="auth/accesstoken"
EPO_API_PUB_DATA="rest-services/published-data"
EPO_API_ENDPOINT_S="search"
EPO_API_ENDPOINT_PUB="publication"
EPO_API_SERVICE_BIB="biblio"
EPO_API_SERVICE_FT="fulltext"

EPO_CONSUMER_KEY=CFG_FILE["token"]["epo_consumer_key"]
EPO_CONSUMER_SECRET_KEY=CFG_FILE["token"]["epo_consumer_secret_key"]

EPO_API_TOKEN_URL=f"{EPO_API_BASE_URL}/{EPO_API_VER}/{EPO_API_TOKEN_URL_SUFIX}"
EPO_API_SEARCH_URL=f"{EPO_API_BASE_URL}/{EPO_API_VER}/{EPO_API_PUB_DATA}/{EPO_API_ENDPOINT_S}/{EPO_API_SERVICE_BIB}"

SEARCH_QUERIES = CFG_FILE["search_config"]["search_queries"]
SEARCH_RANGE = CFG_FILE["search_config"]["range"]
SEARCH_QUERIES_LIST = [build_data_search_q_param(SEARCH_QUERIES[i]) for i in SEARCH_QUERIES]
JOINED_SEARCH_QUERY = join_search_queries(SEARCH_QUERIES_LIST)

NO_DATA_FLAG = "_noData_"
DATA_FORMAT_ERROR_FLAG = "_formErr_"
DTTM = datetime.now().strftime("%s")

####################
# GET ACCESS TOKEN #
####################

access_token_headers = {
    "Content-Type":"application/x-www-form-urlencoded",
    "Accept":"application/json"
}

access_token_body={
    "grant_type":"client_credentials"
}

epo_token_request = requests.post(
    url = EPO_API_TOKEN_URL,
    headers=access_token_headers,
    auth = (
        EPO_CONSUMER_KEY, EPO_CONSUMER_SECRET_KEY
    ),
    data = access_token_body
)

if epo_token_request.status_code == 200:
    EPO_TMP_ACCESS_TOKEN=epo_token_request.json()["access_token"]
else:
    print(f"EPO api status code {epo_token_request.status_code}")
    print(f"EPO api error message {epo_token_request.text}")
    sys.exit(0)
    
########################
# PERFORM SEARCH QUERY #
########################

data_search_headers = {
    "Authorization": f"Bearer {EPO_TMP_ACCESS_TOKEN}",
    "Accept": "application/xml"
}

data_search_params = {
    "q": JOINED_SEARCH_QUERY,
    "Range":SEARCH_RANGE
}

epo_data_request = requests.get(
    url = EPO_API_SEARCH_URL,
    headers=data_search_headers,
    params=data_search_params
)

data_json = convert_xml_to_json(epo_data_request.text)

####################
# CREATE PANDAS DF #
####################

search_output_objects = data_json['ops:world-patent-data']['ops:biblio-search']['ops:search-result']['exchange-documents']

columns = ["doc_number", "issue_date", "applicant-name", "inventor-name", "abstract_lang", "abstract"]

data = []
for i in search_output_objects:
    data_tmp=[]
    try:
        data_tmp.append(i['exchange-document']['bibliographic-data']['publication-reference']['document-id'][1]['doc-number'])
    except:
        data_tmp.append(NO_DATA_FLAG)
    try:
        data_tmp.append(i['exchange-document']['bibliographic-data']['publication-reference']['document-id'][1]['date'])
    except:
        data_tmp.append(NO_DATA_FLAG)
    try:
        data_tmp.append(i['exchange-document']['bibliographic-data']['parties']['applicants']['applicant'][0]['applicant-name']['name'])
    except:
        data_tmp.append(NO_DATA_FLAG)
    try:
        data_tmp.append(i['exchange-document']['bibliographic-data']['parties']['inventors']['inventor'][0]['inventor-name']['name'])
    except:
        data_tmp.append(NO_DATA_FLAG)
    try:
        data_tmp.append(i['exchange-document']['abstract']['@lang'])
    except:
        data_tmp.append(NO_DATA_FLAG)
    try:
        data_tmp.append(i['exchange-document']['abstract']['p'])
    except:
        data_tmp.append(NO_DATA_FLAG)
    data.append(data_tmp)
    
df = pd.DataFrame(data=data, columns=columns)
df.rename({"issue_date":"issue_date_str"}, axis='columns', inplace=True)

df["issue_date"] = df["issue_date_str"].map(lambda x: conv_date_to_sql_comp(x))

df = df[columns]

data_full_txt_headers = {
    "Authorization": f"Bearer {EPO_TMP_ACCESS_TOKEN}", 
    "Accept": "application/fulltext+xml"
}

full_txt_flg_list=[]
for i in df["doc_number"]:
    full_txt_flg_list.append(fulltxt_avail_flg(i, "epodoc", data_full_txt_headers))
    
df["full_txt_flg"] = full_txt_flg_list

df.to_csv(f"data/search_results_{DTTM}.csv", sep=";", header=False, index=False)