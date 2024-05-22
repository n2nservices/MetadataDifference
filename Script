import json
import requests
def make_api_call(url, auth_url, api_key, company_id):
    auth_response = requests.post(auth_url, headers={'Authorization': api_key, 'companyId': company_id}).json()
    access_token = auth_response['token']
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    return response.json()
def sort_json(json_data, sort_key):
    if isinstance(json_data, list):
        json_data.sort(key=lambda x: x.get(sort_key, ""))
        for item in json_data:
            sort_json(item, sort_key)
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == sort_key and isinstance(value, list):
                value.sort()
            sort_json(value, sort_key)
def find_differences(response1, response2):
    differences = {}
    def compare_objects(obj1, obj2, current_key=""):
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            for key in set(obj1) - set(obj2):
                differences[current_key + key] = {
                    "qa_response": obj1[key],
                    "prod_response": None
                }
            for key in set(obj2) - set(obj1):
                differences[current_key + key] = {
                    "qa_response": None,
                    "prod_response": obj2[key]
                }
            for key in set(obj1) & set(obj2):
                compare_objects(obj1[key], obj2[key], current_key + key + ".")
        elif isinstance(obj1, list) and isinstance(obj2, list):
            if len(obj1) != len(obj2):
                differences[current_key] = {
                    "qa_response": obj1,
                    "prod_response": obj2
                }
            else:
                for i in range(len(obj1)):
                    compare_objects(obj1[i], obj2[i], current_key + f"[{i}].")
        else:
            if obj1 != obj2:
                differences[current_key] = {
                    "qa_response": obj1,
                    "prod_response": obj2
                }
    compare_objects(response1, response2)
    return differences
def compare_json_objects(obj1, obj2, current_key="", differences=None):
    if differences is None:
        differences = {}
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        for key in set(obj1) | set(obj2):
            compare_json_objects(obj1.get(key), obj2.get(key), current_key + key + ".", differences)
    elif isinstance(obj1, list) and isinstance(obj2, list):
        if len(obj1) != len(obj2):
            differences[current_key[:-1]] = {
                "qa_response": obj1,
                "prod_response": obj2
            }
        else:
            for i in range(len(obj1)):
                compare_json_objects(obj1[i], obj2[i], current_key + f"[{i}].", differences)
    else:
        if obj1 != obj2:
            differences[current_key[:-1]] = {
                "qa_response": obj1,
                "prod_response": obj2
            }
    return differences
def main():
    qa_base_url = 'https://qa.illuminateapp.com/atom'
    qa_auth_url = 'https://qa.illuminateapp.com/v1/auth'
    prod_base_url = 'https://illuminateapp.com/atom'
    prod_auth_url = 'https://illuminateapp.com/v1/auth'
    qa_api_key = '1c8a39ae-fa05-4e15-a3bb-1a1199d0e67c'
    qa_company_id = 'T5L'
    prod_api_key = 'fe2e017f-2a0e-4870-b28f-41825df9609b'
    prod_company_id = '4KU'
    api_names = ['SectionInfoStatus', 'createenrollment', 'accountledgerentry']
    qa_responses = []
    prod_responses = []
    for api_name in api_names:
        qa_metadata_api_url = f'{qa_base_url}?location={qa_company_id}&apiKey={qa_api_key}&apiName={api_name}'
        prod_metadata_api_url = f'{prod_base_url}?location={prod_company_id}&apiKey={prod_api_key}&apiName={api_name}'
        # Make QA Auth call and Metadata call
        qa_response = make_api_call(qa_metadata_api_url, qa_auth_url, qa_api_key, qa_company_id)
        qa_responses.append(qa_response)
        # Make prod Auth call and Metadata call
        prod_response = make_api_call(prod_metadata_api_url, prod_auth_url, prod_api_key, prod_company_id)
        prod_responses.append(prod_response)
    for i in range(len(api_names)):
        print(f'Differences for API: {api_names[i]}')
        qa_response = qa_responses[i]
        prod_response = prod_responses[i]
        sort_json(qa_response, "responseName")
        sort_json(prod_response, "responseName")
        differences = compare_json_objects(qa_response, prod_response)
        differing_values = {
            key: value for key, value in differences.items()
            if isinstance(value, dict) and value["qa_response"] != value["prod_response"]
        }
        # Exclude positional differences
        differing_values = {
            key: value for key, value in differing_values.items()
            if not key.endswith(".apiResponseName") and not key.endswith(".dataTranslationName")
        }
        if differing_values:
            print(json.dumps(differing_values, indent=4))
        else:
            print("No differences found.")
main()
