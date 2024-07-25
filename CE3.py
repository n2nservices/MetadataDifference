import json
import requests


def make_api_call(url, auth_url, api_key, company_id, accept_header=None, additional_headers=None):
    headers = {'Authorization': api_key, 'companyId': company_id}
    if accept_header:
        headers['Accept'] = accept_header
    if additional_headers:
        headers.update(additional_headers)

    auth_response = requests.post(auth_url, headers=headers).json()
    access_token = auth_response['token']
    headers = {'Authorization': access_token}

    response = requests.get(url, headers=headers)
    return response.json()


def make_idw_api_call(url, auth_url, api_key, company_id, accept_header=None, additional_headers=None):
    headers = {'Authorization': api_key, 'companyId': company_id}
    if accept_header:
        headers['Accept'] = accept_header

    auth_response = requests.post(auth_url, headers=headers).json()
    access_token = auth_response['token']

    # Additional headers specific to IDW API, including access token
    idw_additional_headers = {
        "Accept": "application/n2n.integration.v2+json",
        "location": company_id,
        "apiKey": api_key,
        "Authorization": access_token  # Use the access token for authorization
    }

    # Update headers with access token
    headers = {'Authorization': access_token}
    headers.update(idw_additional_headers)

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


def save_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    qa_base_url = 'https://qa.illuminateapp.com/atom'
    qa_auth_url = 'https://qa.illuminateapp.com/v1/auth'
    prod_base_url = 'https://illuminateapp.com/atom'
    prod_auth_url = 'https://illuminateapp.com/v1/auth'
    qa_api_key = 'f602a5f2-1486-4231-af27-ae9525ea541c'
    qa_company_id = 'G2H'
    prod_api_key = 'fb82971d-4a13-4b20-9e0c-22a25cc6578b'
    prod_company_id = 'YIO'
    api_names = ['courseAuditInternal', 'registeredCoursesInternal', 'dropRegisteredCourse', 'registerStudents',
                 'createenrollment', 'updateEnrollment', 'accountLedgerEntry', 'person_courseAudit',
                 'academicPeriod_courseAudit', 'sectionRegistration_courseAudit', 'section_courseAudit',
                 'person_registeredCourse', 'academicPeriod_registeredcourse', 'sectionRegistration_registeredCourse',
                 'section_registeredCourse', 'persons_accountLedgerEntry', 'academicPeriods_accountLedgerEntry',
                 'accountingcodes_accountLedgerEntry', 'studentspayments_accountLedgerEntry',
                 'persons_dropregistrationCourse', 'academicPeriods_dropRegistrationscourse',
                 'sectionRegistrations_dropRegistrations', 'section_dropregistrationscourse',
                 'sectionRegistration_upsert_dropRegistartions', 'validateaerinput', 'createupdateperson',
                 'persons_createEnrollment', 'academicPeriods_createEnrollment', 'sites_createEnrollment',
                 'regions_createEnrollment', 'countries_createEnrollment', 'persons_post_createEnrollment',
                 'admissionapplications_Colleague_createEnrollement', 'Residencytypes_createEnrollment',
                 'admissionapplications_post_createEnrollment', 'admissionDecesions_createEnrollment',
                 'validateaerinput_updateEnrollment', 'createupdateperson_updateEnrollment', 'persons_updateEnrollment',
                 'academicPeriods_updateEnrollment', 'sites_updateEnrollment', 'regions_updateEnrollment',
                 'countries_updateEnrollment', 'persons_put_updateEnrollment',
                 'admissionapplications_Colleague_updateEnrollment', 'Residencytypes_updateEnrollment',
                 'admissionapplications_post_updateEnrollment', 'admissionDecesions_updateEnrollment']
    IDW_api = ['courseaudit_internal', 'registeredcourses_internal', 'dropregistrations_internal',
               'registerstudents_internal', 'accountledgerentry_internal', 'createenrollment_collegue_internal',
               'updateenrollment_collegue_internal', 'upsertregistration', 'validateaerinput_internal',
               'createupdateperson_internal', 'admissionapplicationsdecesion_collegue_createenrollment',
               'admissionapplicationsdecesion_collegue_updateenrollment', 'validateaerinput_updateenrollment_internal']

    all_qa_responses = []
    all_prod_responses = []

    for i, api_name in enumerate(api_names):
        print(f'Differences for API: {api_name}')
        qa_metadata_api_url = f'{qa_base_url}?location={qa_company_id}&apiKey={qa_api_key}&apiName={api_name}'
        prod_metadata_api_url = f'{prod_base_url}?location={prod_company_id}&apiKey={prod_api_key}&apiName={api_name}'

        print("QA Metadata API URL:", qa_metadata_api_url)
        print("Prod Metadata API URL:", prod_metadata_api_url)

        # Make QA Auth call and Metadata call
        qa_response = make_api_call(qa_metadata_api_url, qa_auth_url, qa_api_key, qa_company_id)
        all_qa_responses.append(qa_response)

        # Make prod Auth call and Metadata call
        prod_response = make_api_call(prod_metadata_api_url, prod_auth_url, prod_api_key, prod_company_id)
        all_prod_responses.append(prod_response)

        try:
            sort_json(qa_response, "responseName")
            sort_json(prod_response, "responseName")
        except AttributeError as e:
            print("AttributeError occurred while sorting JSON:", e)

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

    for i, api_name in enumerate(IDW_api):
        print(f'Differences for API: {api_name}')
        qa_metadata_api_url = f'{qa_base_url}?method=POST&apiName={api_name}'
        qa_headers = {"location": qa_company_id, "apiKey": qa_api_key, "Authorization": qa_response,
                      "Accept": "application/n2n.integration.v2+json"}

        prod_metadata_api_url = f'{prod_base_url}?method=POST&apiName={api_name}'
        prod_headers = {"location": prod_company_id, "apiKey": prod_api_key, "Authorization": prod_response,
                        "Accept": "application/n2n.integration.v2+json"}

        print("QA Metadata API URL:", qa_metadata_api_url)
        print("Prod Metadata API URL:", prod_metadata_api_url)

        # Make QA Auth call and Metadata call with additional headers
        qa_response = make_idw_api_call(qa_metadata_api_url, qa_auth_url, qa_api_key, qa_company_id, accept_header=None,
                                        additional_headers=qa_headers)

        all_qa_responses.append(qa_response)
        print(qa_response)

        # Make prod Auth call and Metadata call with additional headers
        prod_response = make_idw_api_call(prod_metadata_api_url, prod_auth_url, prod_api_key, prod_company_id,
                                          accept_header=None, additional_headers=prod_headers)
        all_prod_responses.append(prod_response)
        print(prod_response)

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

    # Save all responses to files
    save_json_to_file(all_qa_responses, 'qa_responses.json')
    save_json_to_file(all_prod_responses, 'prod_responses.json')


main()
