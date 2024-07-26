import time 
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return f"I'm Alive... Fuck Off {time.time()}"

def run():
  app.run(host='0.0.0.0',port=80)

def keep_alive():  
    t = Thread(target=run)
    t.start()


