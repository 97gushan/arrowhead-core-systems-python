import json
from requests_pkcs12 import get, post

with open("config_template.json") as json_file:
    config = json.load(json_file)[0]
    pkcs12_filename = config["certificate_info"]["pkcs12_filename"]
    pkcs12_password = config["certificate_info"]["pkcs12_password"]
    service_regisrty_url = config["urls"]["service_regisrty_url"]
    authorization_url = config["urls"]["authorization_url"]
    orchestration_url = config["urls"]["orchestration_url"]
    consumer_json = config["consumer_json"]
    consumer_name = config["consumer_json"]["systemName"]
    provider_json = config["provider_json"]
    provider_name = config["provider_json"]["systemName"]
    service_definition_json = config["consumer_json"]
    service_definition = config["service_definition_json"]["serviceDefinition"]


def register_system(json):
    url = service_regisrty_url + "/mgmt/systems"
    return post(url,
                verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password, json=json
                )


def register_service(json):
    url = service_regisrty_url + "/mgmt"
    return post(url,
                verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password, json=json
                )


def get_services():
    url = service_regisrty_url + "/mgmt?direction=ASC"
    return get(url,
               verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password
               )


def get_systems():
    url = service_regisrty_url + "/mgmt/systems?direction=ASC&sort_field=id"
    return get(url,
               verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password
               )


def find_system_ids(consumer_name, provider_name):
    response = get_systems()
    for system in response.json()["data"]:
        if system["systemName"] == consumer_name:
            consumer_id = system["id"]
        elif system["systemName"] == provider_name:
            provider_id = system["id"]
    return [consumer_id, provider_id]


def find_service_id(service_definition):
    response = get_services()
    for service in response.json()["data"]:
        if service["serviceDefinition"]["serviceDefinition"] == "service_provider":
            interface_id = service["interfaces"][0]["id"]
            service_definition_id = service["id"]
    return [service_definition_id, interface_id]


def create_authorization_json():
    idarray = find_system_ids(consumer_name, provider_name) + \
        find_service_id(service_definition)
    authorization_json = {
        "consumerId": idarray[0],
        "interfaceIds": [
            idarray[3]
        ],
        "providerIds": [
            idarray[1]
        ],
        "serviceDefinitionIds": [
            idarray[2]
        ]
    }
    return authorization_json


def add_intracloud_authorization():
    url = authorization_url + "/mgmt/intracloud"
    authorization_json = create_authorization_json()
    return post(url,
                verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password, json=authorization_json
                )


def create_orchestration_json():
    idarray = find_system_ids(consumer_name, provider_name)
    orchestration_json = [
        {
            "serviceDefinitionName": "service_provider",
            "consumerSystemId": idarray[0],
            "providerSystem": {
                "systemName": "aimbot_provider",
                "address": "https://benkpress.ltu.campus.se",
                "port": 1235,
                "authenticationInfo": ""
            },
            "cloud": {
                "operator": "aitia",
                "name": "testcloud2"
            },
            "serviceInterfaceName": "HTTPS-SECURE-JSON",
            "priority": 1
        }
    ]
    return orchestration_json


def create_orchestration_store_entry():
    url = orchestration_url + "/mgmt/store"
    orchestration_json = create_orchestration_json()
    return post(url,
                verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password, json=orchestration_json
                )


def start_orchestration_based_on_id():
    consumer_id = find_system_ids(consumer_name, provider_name)[0]
    url = orchestration_url + "/orchestration/" + str(consumer_id)
    return get(url,
               verify=False, pkcs12_filename=pkcs12_filename, pkcs12_password=pkcs12_password
               )


# Register consumer
print(register_system(consumer_json).json())
# Register provider
register_system(consumer_json).json()
# Add service definition
register_service(service_definition_json).json()
# Add intra-cloud authorization
add_intracloud_authorization().json()
# Create orchestration store entry
create_orchestration_store_entry().json()
#  Start orchestration based on consumer id.
start_orchestration_based_on_id().json()

# Add your own application code below
