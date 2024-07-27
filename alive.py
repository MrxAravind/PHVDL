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
        text = logfile.readlines()
        log = []
        for i in range(-1,len(text)):
            log.append(text[i])
             
        return "<br>".join(log)
    
def run():
  app.run(host='0.0.0.0',port=80)

def keep_alive():  
    t = Thread(target=run)
    t.start()


