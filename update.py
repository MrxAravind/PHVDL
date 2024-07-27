import asyncio
import requests
from bs4 import BeautifulSoup
import json
import time
from config import *
import random 
from database import *
import logging







database_name = "Spidydb"
db = connect_to_mongodb(DATABASE, database_name)
collection_name = "PHVDL"

# Configure logging
logging.basicConfig(
    filename='link_fetcher.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def get_info():
    documents = find_documents(db, collection_name)
    urls = [doc["URL"] for doc in documents]
    return urls



def fetch_video_links():
    base_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
    url = "https://www.pornhub.com"
    search_url = "https://www.pornhub.com/video/search?search="
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(base_url + url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0] for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')]


def search_video_links(query):
    base_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
    search_url = "https://www.pornhub.com/video/search?search="
    url = "https://www.pornhub.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(base_url + search_url + query, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0] for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')]


def send_message(text,chat_id):
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        response = requests.post(url, data=payload)
        logging.info(response.json())


words =["blowjob","step_sister","step_mom","familysharing","Swap_sister","swap_mom","bdsm","anal","pussy licking","transgender",
        "gangbang","dp","breastfeeding","MLIF","japanese","deepthroat","rimming","tits","boobs",
        "milking","facial","freeuse","Lesbian","Latina","Bondage","Natural Tits","kink","squirting", "bukkake","Cuckold","Orgy","cock", "pussy", "vagina","Threesome","cuckquean", "cream pie","swallow cum","Hotwives","TiedUp","69"]

nsfw_keywords = [
    "nsfw", "explicit", "nude", "porn", "sex", "xxx", "hentai", "erotic", 
    "fetish", "bdsm", "hardcore", "anal", "blowjob", "cum", "ejaculation", 
    "masturbation","Breastfeeding","pussy licking" ,"orgasm", "penetration", "intercourse", "adult video", 
    "sex tape", "adult toys", "sex chat", "sex cam", "nude pics", "free porn", 
    "amateur porn", "anal sex", "gay porn", "lesbian porn", "shemale", "tranny", 
    "tits", "boobs", "naked", "striptease", "strip club", "escort", "call girl", 
    "sex worker", "prostitute", "sex addict", "gangbang", "threesome", "swingers", 
    "sex party", "sexual fantasy", "erotic massage", "sex position", "bondage", 
    "domination", "submission", "roleplay", "cosplay sex", "voyeur", "exhibitionist", 
    "scat", "watersports", "fisting", "gloryhole", "cock", "pussy", "vagina", "penis", 
    "dildo", "vibrator", "anal beads", "butt plug", "sex doll", "sex swing", "orgy", 
    "cumshot", "facial", "deepthroat", "rimming", "rimjob", "squirting", "bukkake", 
    "foot fetish", "foot job", "tickling", "spanking", "kink", "kinkster", "leather", 
    "latex", "rubber", "gimp", "chastity", "cuckold", "cuckquean", "cream pie", "felching", 
    "sounding", "pegging", "zoophilia", "bestiality", "necrophilia", "pedophilia", "child porn", 
    "cp", "hentai", "futanari", "yaoi", "yuri", "shota", "loli", "ero", "eroge", "bishoujo", 
    "bishonen", "hentai doujin", "doujinshi", "smut", "lemon", "lime", "yaoi paddle", "furry porn", 
    "anthro porn", "monster porn", "tentacle porn", "hentai game", "h-game", "visual novel", "ecchi", 
    "super ecchi", "oppai", "yiff", "bara", "ahegao", "pissing", "piss play", "golden shower",
]


def main():
  while True:
    urls = []
    for i in range(10):
        word=  random.choice(words)
        logging.info(word)
        qurls = search_video_links(word)
        urls.extend(qurls)
    urls.extend(fetch_video_links())
    length = len(urls)
    logging.info("Total Videos:"+length)
    data = get_info()
    urls = [url for url in urls if url not in data]
    filtered = len(urls)
    logging.info("Filtered Videos:"+length)
    urls = random.sample(urls,60)
    urls = [" ".join(urls[0:30])," ".join(urls[30:])]
    for url in urls:
           send_message(text=url,chat_id=LINK_ID)
           logging.info("Splited Videos:"+str(len(url.split())))
           send_message(text=f"Total {length} Videos\nFiltered {filtered}\nNow Sent {len(url.split())}",chat_id=LOG_ID)
           time.sleep(1200)
    time.sleep(3600)



if __name__ == '__main__':
    main()
