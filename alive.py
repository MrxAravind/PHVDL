from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
  app.run(host='0.0.0.0',port=80)

def keep_alive():  
    t = Thread(target=run)
    t.start()


def fetch_video_links():
    base_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
    url = "https://www.pornhub.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(base_url + url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0] for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')]

def send_message(urls):
    bot = telegram.Bot(BOT_TOKEN)
    bot.send_message(text=" ".join(urls), chat_id=LOG_ID)

def link_gen():
    while True:
        urls = fetch_video_links()
        send_message(urls)
        time.sleep(3600)  # Sleep for 1 hourdef keep_alive():  
   
    
def autobot():  
    t = Thread(target=link_gen)
    t.start()

