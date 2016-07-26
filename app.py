import os
import sys
import json
import requests

import requests
from flask import Flask, request
from bs4 import BeautifulSoup

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAJG8qmr7RABAPh5BY3aSFe2gIkQxtMv5lqth5k4nfLlJNfqYly9lGpqrw88ZBjIP7pzZBRd64KLtPlqtYjolOTWpZCPv5coWzIhJa2dfWxRCyEsZAFTC1SiZAHvwIiMJ0BZA7auNkjZC5ZC5ZBpuVMAoCGy80pGOchnn46C4CfUdNwZDZD"
VERIFY_TOKEN      = "jiten803"
BASE_URL = "https://www.youtube.com"
BASE_QUERY = "https://www.youtube.com/results?search_query="
DEFAULT_MESSAGE = "Sorry! Unable to search"
WELCOME_MESSAGE = "Hey there!\n To search for videos type the title of the video."
@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, get_video(message_text))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def get_video(message_text):
    BASE_TAG = message_text.replace(' ','+')
    QUERY    = BASE_QUERY + BASE_TAG
    response = requests.get(QUERY)  
    soup     = BeautifulSoup(response.text, "html.parser")
    #prininternal_link = soup.select_one('a[href^="/watch?v"]')
    img      = soup.select_one('img[src^="https://i.ytimg.com/vi"]')
    headings = soup.select(".yt-lockup-title")
    anchor   = None
    for heading in headings :
        anchor = heading.contents[0]
        if anchor['href'].startswith('/watch?v='):
            break
    
    print(img['src'])
    print(anchor['href'])
    #print(anchor['title'])
    url = {
    "video" : BASE_URL + anchor['href'],
    "img" : img['src'],
    "title" : anchor['title'],
    }
    return url 


def send_message(recipient_id, url):

    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=url{'title'}))

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "setting_type" : "greeting",
        "greeting" : {
            "text" : "Welcome! Just type name of a song and the bot will give you a video link."
        },
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment" : {
            "type": "template",
            "payload" : {
                "template_type" : "generic",
                "elements" : [
                {
                    "title" : url['title'],
                    "image_url" : url['img'],
                    "buttons" : [
                    {
                        "type":"web_url",
                        "url" : url['video'],
                        "title": "Visit Youtube!",
                    }]
                }]
            }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
