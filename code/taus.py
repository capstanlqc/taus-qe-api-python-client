import os
import sys
import requests
import json
from dotenv import load_dotenv
import pprint

load_dotenv()
TAUS_API_KEY = os.environ["TAUS_API_KEY"]


def validate_dict(data, schema):
    """
    Recursively validate a dictionary against a schema.

    :param data: The dictionary to validate.
    :param schema: The schema that defines the expected structure.
    :return: True if valid, False otherwise.
    """
    if isinstance(schema, dict):
        if not isinstance(data, dict):
            print(f"Expected dict, got {type(data).__name__}")
            return False

        for key, value_type in schema.items():
            if key not in data:
                print(f"Missing key: {key}")
                return False

            if not validate_dict(data[key], value_type):
                print(f"Invalid structure or type for key: {key}")
                return False

    elif isinstance(schema, list):
        if not isinstance(data, list):
            print(f"Expected list, got {type(data).__name__}")
            return False

        if len(schema) != 1:
            print("Schema list should have exactly one element")
            return False

        # Validate each item in the list
        item_schema = schema[0]
        for item in data:
            if not validate_dict(item, item_schema):
                print(f"Invalid list item: {item}")
                return False

    else:
        # Base case: check if data matches the type
        if not isinstance(data, schema):
            print(
                f"Incorrect type. Expected {schema.__name__}, got {type(data).__name__}"
            )
            return False

    return True


schema = {
    "source": {"value": str, "language": str},
    "targets": [{"value": str, "language": str}],
    "metrics": [{"uid": str, "version": str}],
}


data = {
    "source": {"value": "This is a test.", "language": "en"},
    "targets": [{"value": "Das ist ein Test.", "language": "de"}],
    "metrics": [{"uid": "taus_qe", "version": "2.0.0"}],
}


def print_dict_as_tree(data):
    pprint.pprint(data, indent=4)
    # print(json.dumps(data, indent=4))


def get_taus_qe(json_data):
    if not validate_dict(data, schema):
        sys.exit("Payload does not have the expected tree structure or key names.")

    url = "https://api.sandbox.taus.net/1.0/estimate"

    # print(f"{type(json_data)=}")
    # print(f"{json_data}")
    payload = json.dumps(json_data)
    headers = {
        "Api-Key": TAUS_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print("results")
    # print(response.text)
    print(f"{json.loads(response.text)['billedCharacters']=}")
    # print(f"{type(response.text)=}")
    return response.text


# x = get_taus_qe(data)

results = {
    "source": {"value": "This is a test.", "language": "en"},
    "estimates": [
        {
            "segment": {"value": "Das ist ein Test.", "language": "de"},
            "metrics": [
                {"uid": "taus_qe", "value": 0.9457928538322449, "version": "2.0.0"}
            ],
        }
    ],
    "billedCharacters": 32,
}


def get_taus_qe_mockup(json_data):
    pprint.pprint(json_data)

    if not validate_dict(data, schema):
        sys.exit("Payload does not have the expected tree structure or key names.")

    payload = json.dumps(json_data)
    print(payload)
    print(f"{type(results)=}")

    return results
