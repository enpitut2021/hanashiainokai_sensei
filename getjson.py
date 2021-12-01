import requests, json
from discordwebhook import Discord

url = requests.get("https://jsonplaceholder.typicode.com/users")
text = url.text

data = json.loads(text)

user = data[0]
print(user['name'])

address = user['address']

discord = Discord(url="https://discord.com/api/webhooks/915450978373881897/YbwIYDF1HtSKbTYkXyZlIcLx1R6IDbXI-7wDM8xMPENLxrufqccVwtKx14T4DYmb74JP")
discord.post(content=address)
print(address)