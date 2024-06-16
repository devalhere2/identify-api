import requests
import json


# Step 2: Read the JSON file
with open('sample.json', 'r') as file:
    data = json.load(file)

responses = []

# Step 3: Iterate over each entry and make a POST request
for entry in data:
    print(entry)
    response = requests.post('http://localhost:8000/identify', json=entry)
    if response.status_code == 200:
        responses.append(response.json())
    else:
        responses.append({'error': 'Failed to process', 'data': entry})

# Step 6: Save the responses into a new JSON file
with open('response.json', 'w') as file:
    json.dump(responses, file, indent=4)