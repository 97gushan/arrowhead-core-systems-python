import json
from requests_pkcs12 import get, post

with open("api.json") as f:
    api = json.load(f)

    urls = api["urls"]
    cert = api["certificate_info"]

with open("consumer.json") as f:
    consumer_service = json.load(f)["service_definition_json"]

with open("producer.json") as f:
    producer_service = json.load(f)["service_definition_json"]


def register_system(json):
    url = urls["service_registry_url"] + "/mgmt/systems"
    return post(url,
                verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"], json=json
                )


def register_service(json):
    url = urls["service_registry_url"] + "/mgmt"
    return post(url,
                verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"], json=json
                )


def get_services():
    url = urls["service_registry_url"] + "/mgmt?direction=ASC"
    return get(url,
               verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"]
               )


def get_systems():
    url = urls["service_registry_url"] + \
        "/mgmt/systems?direction=ASC&sort_field=id"
    return get(url,
               verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"]
               )


def find_system_ids(consumer_name, provider_name):
    response = get_systems()
    provider_id = {}
    consumer_id = {}
    for system in response.json()["data"]:
        if system["systemName"] == consumer_name:
            consumer_id = system["id"]
        elif system["systemName"] == provider_name:
            provider_id = system["id"]
    return consumer_id, provider_id


def find_service_id(service_definition):
    response = get_services()
    service_definition_id = {}
    interface_id = {}
    for service in response.json()["data"]:
        if service["serviceDefinition"]["serviceDefinition"] == service_definition:
            interface_id = service["interfaces"][0]["id"]
            service_definition_id = service["id"]
    return service_definition_id, interface_id


def create_authorization_json(consumer, producer):
    consumer_id, provider_id = find_system_ids(consumer, producer)
    service_definition_id, interface_id = find_service_id("hello-consumer")
    authorization_json = {
        "consumerId": consumer_id,
        "providerIds": [provider_id],
        "interfaceIds": [interface_id],
        "serviceDefinitionIds": [service_definition_id]
    }
    return authorization_json


def add_intracloud_authorization():
    url = urls["authorization_url"] + "/mgmt/intracloud"
    authorization_json = create_authorization_json("consumer", "producer")
    return get(url,
               # , json=authorization_json
               verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"]
               )


def create_orchestration_json(consumer, producer):
    consumer_id, _ = find_system_ids(consumer, producer)
    orchestration_json = [
        {
            "serviceDefinitionName": producer_service["serviceDefinition"],
            "consumerSystemId": consumer_id,
            "providerSystem": producer_service["providerSystem"],
            "cloud": {
                "operator": "aitia",
                "name": "testcloud2"
            },
            "serviceInterfaceName": "HTTPS-SECURE-JSON",
            "priority": 1
        }
    ]
    return orchestration_json


def create_orchestration_store_entry(consumer, producer):
    url = urls["orchestration_url"] + "/mgmt/store"
    orchestration_json = create_orchestration_json(consumer, producer)
    print(orchestration_json)
    return post(url,
                verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"], json=orchestration_json
                )


def get_orchestration():
    url = urls["orchestration_url"] + "/mgmt/store"
    return get(url,
               verify=False, pkcs12_filename=cert["pkcs12_filename"], pkcs12_password=cert["pkcs12_password"]
               )


def start_orchestration():
    consumer_id, producer_id = find_system_ids("consumer", "producer")
    resp = get_orchestration().json()

    for r in resp["data"]:
        if r["consumerSystem"]["id"] == consumer_id:
            return r


# register producer
# print(producer_service)
# print(register_system(producer_service["providerSystem"]).json())
# print(register_service(producer_service).json())

# register consumer
# print(consumer_service)
# print(register_system(consumer_service["providerSystem"]).json())
# print(register_service(consumer_service).json())


# check so both systems are up
# print(get_systems().json())
# print(find_system_ids("consumer", "producer"))
# print(find_service_id("hello-consumer"))
# print(json.dumps(get_services().json(), indent=4, sort_keys=True))

# create intracloud auth
# print(create_authorization_json("consumer", "producer"))
# print(add_intracloud_authorization().json())

# create orchestration entry
# print(create_orchestration_json("consumer", "producer"))
# print(create_orchestration_store_entry("consumer", "producer").json())

# start orchestration/ get system information (ip:port and other stuff)
# print(json.dumps(start_orchestration(), indent=4, sort_keys=True))
