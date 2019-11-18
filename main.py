from github_webhook import Webhook
from flask import Flask
from pprint import pprint
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
webhook = Webhook(app) # Defines '/postreceive' endpoint

@webhook.hook()
def on_push(data):
    print("Got push with: {0}".format(data))

@webhook.hook(event_type="issues")
def on_issues(data):
    print("Got issue with: {0}".format(data))
    pprint(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
