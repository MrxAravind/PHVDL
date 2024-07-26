import asyncio
import telegram
import requests
from bs4 import BeautifulSoup
import json
import time
from config import *


def fetch_video_links():
    base_url = "https://cf-proxy.mrspidyxd.workers.dev/?host="
    url = "https://www.pornhub.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(base_url + url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [div.find('a', class_='thumbnailTitle')['href'].replace("https://cf-proxy.mrspidyxd.workers.dev", url).split("&")[0] for div in soup.find_all('div', class_='vidTitleWrapper') if div.find('a', class_='thumbnailTitle')]




async def main():
  while True:
    await asyncio.sleep(30)
    urls = fetch_video_links()
    length = len(urls)
    urls = [" ".join(urls[0:30])," ".join(urls[30:-1])]
    bot = telegram.Bot(BOT_TOKEN)
    async with bot:
        for url in urls:
           await bot.send_message(text=url,chat_id=DUMP_ID)
            await asyncio.sleep(600)
           await bot.send_message(text=f"{len(url.split())} out of {length} Videos has Been Sent",chat_id=LOG_ID)
    await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())
