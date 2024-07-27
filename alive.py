import time
from flask import Flask
from threading import Thread
from datetime import datetime


app = Flask('')

@app.route('/')
def home():
    return f"I'm Alive... Fuck Off {datetime.now()}"


@app.route('/logs')
def logs():
    file = "video_downloader.log"
    with open(file) as logfile:
        log = logfile.readlines()     
        return f"""<h6>{"<h6><br><h6>".join(log)}<h6>"""
  
@app.route('/links')
def links():
    file = "link_fetcher.log"
    with open(file) as logfile:
        log = logfile.readlines()  
        return f"""<h6>{"<h6><br><h6>".join(log)}<h6>"""


def run():
  app.run(host='0.0.0.0',port=80)

def keep_alive():  
    t = Thread(target=run)
    t.start()


