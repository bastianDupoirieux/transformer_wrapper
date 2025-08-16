import requests

review = "This is a great product! I love it."

response = requests.post("http://127.0.0.1:8000/", json=review)
print(response.text)