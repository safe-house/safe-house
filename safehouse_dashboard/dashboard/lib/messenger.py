import re
from fbchat import Client
from fbchat.models import *
import requests
from bs4 import BeautifulSoup
import urllib.request


def send_message(msg, user_id):
    client = Client('safehousestartup@gmail.com', 'safehouse_2019')
    sent = client.sendMessage(msg, thread_id=user_id)
    if sent:
        return "Message Sent"
    else:
        return "An error occurred"


def get_facebook_id(fb_url):
    url = "https://findmyfbid.com/"
    params = {'url': fb_url}
    try:
        r = requests.post(url=url, params=params)
        return r.json().get("id")
    except AttributeError:
        html_page = urllib.request.urlopen(fb_url)
        soup = BeautifulSoup(html_page, "html.parser")
        for link in soup.findAll('a', attrs={'ajaxify': re.compile("^/ajax/timeline/")}):
            link = link.get('ajaxify')
            for i in range(0, len(link)):
                if link[i] == "d" and link[i + 1] == "=":
                    user_id = link[i + 2:i + 17]
            return user_id
