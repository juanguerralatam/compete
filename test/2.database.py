# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import requests

PORT = 9000

def test_database_operations(port):
    test_data = {
        'brand': 'TestBrand',
        'fix_cost': 1000,
        'variable_cost': 50,
        'capital': 50000
    }

    # Test CREATE
    try:
        create_response = requests.post(
            f"http://localhost:{port}/basic_info/",
            json=test_data
        )
        print(f"[Port {port}] Create response:", create_response.status_code)
        created_id = create_response.json()['id']
    except Exception as e:
        print(f"[Port {port}] Create failed:", str(e))
        return

    # Test READ
    try:
        get_response = requests.get(f"http://localhost:{port}/basic_info/{created_id}/")
        print(f"[Port {port}] Read response:", get_response.status_code)
        print("Retrieved data:", json.dumps(get_response.json(), indent=2))
    except Exception as e:
        print(f"[Port {port}] Read failed:", str(e))

    # Test UPDATE
    try:
        update_data = {'fix_cost': 1500}
        update_response = requests.patch(
            f"http://localhost:{port}/basic_info/{created_id}/",
            json=update_data
        )
        print(f"[Port {port}] Update response:", update_response.status_code)
    except Exception as e:
        print(f"[Port {port}] Update failed:", str(e))

    # Test DELETE
    try:
        delete_response = requests.delete(f"http://localhost:{port}/basic_info/{created_id}/")
        print(f"[Port {port}] Delete response:", delete_response.status_code)
    except Exception as e:
        print(f"[Port {port}] Delete failed:", str(e))

# Test both database instances
if __name__ == "__main__":
    print(f"Testing first database (Port {PORT})")
    test_database_operations(PORT)
    
    print(f"\nTesting second database (Port {PORT+1})")
    test_database_operations(PORT+1)