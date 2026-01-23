#!/usr/bin/env python3
import requests
import json

url = "http://localhost:58247/api/create_session"
payload = {
    "room_name": "Test Room",
    "broadcaster_name": "Tester"
}

response = requests.post(url, json=payload)
data = response.json()

print("Status Code:", response.status_code)
print("\nResponse Keys:", list(data.keys()))
print("\nHas qr_code:", "qr_code" in data)

if "qr_code" in data:
    qr_code = data["qr_code"]
    print("QR Code Present: YES")
    print("QR Code Length:", len(qr_code))
    print("First 100 chars:", qr_code[:100])
    print("Starts with 'data:image':", qr_code.startswith("data:image"))
else:
    print("QR Code Present: NO")
    print("\nFull response:")
    print(json.dumps(data, indent=2))
