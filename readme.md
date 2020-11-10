# Arrowhead core service registration using python.

## Prerequisites:
* A working local arrowhead cloud.
* Python 3 with requests_pkcs12 and json installed.

## How to use:
Copy the config_template_json and replace the
* pkcs12_filename with the path to your own .p12 file.
* pkcs12_password with your own password.

to match your own certificate. 

For info on how to create your own certificates please read [java client skeleton]()

Replace the consumer, provider and service definition jsons in your own config file to match your own systems.

## TODO
Add support for dynamic orchestration.
