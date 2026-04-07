"""
Test if tasks API endpoint is working
"""
import requests

try:
    # Test login first
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        data={
            "username": "admin@opsit.com",
            "password": "admin123"
        }
    )

    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"Login successful. Token: {token[:20]}...")

        # Test tasks API
        headers = {"Authorization": f"Bearer {token}"}
        tasks_response = requests.get(
            "http://localhost:8000/api/v1/tasks/?sys_class_name=incident&assigned_to_my_groups=true",
            headers=headers
        )

        print(f"\nTasks API Status: {tasks_response.status_code}")

        if tasks_response.status_code == 200:
            data = tasks_response.json()
            print(f"Total tasks: {data.get('total', 0)}")
            print(f"Tasks returned: {len(data.get('tasks', []))}")
            for task in data.get('tasks', [])[:3]:
                print(f"  - {task['number']}: {task['short_description']}")
        else:
            print(f"Error: {tasks_response.text}")
    else:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)

except Exception as e:
    print(f"Error: {e}")
