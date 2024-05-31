from email import header
import requests, pprint


user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;'}
response = requests.get('http://localhost:8024/api/datetime/', headers=user_agent)

print(response.status_code)
print(response.ok)
pprint.pprint(response.headers)
pprint.pprint(response.request.headers)
