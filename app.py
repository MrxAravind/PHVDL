import os
import logging
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
import asyncio 
from datetime import datetime
import time
from speed import *
from alive import keep_alive 
from config import *
from database import *
import static_ffmpeg
from sysinfo import *

database_name = "Spidydb"
db = connect_to_mongodb(DATABASE, database_name)
collection_name = "PHVDL"

# Uncomment if needed
static_ffmpeg.add_paths()
keep_alive()

# Configure logging
logging.basicConfig(
    filename='video_downloader.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def check_db(url):
    documents = find_documents(db, collection_name)
    logging.info("Documents retrieved from MongoDB:")
    urls = [doc["URL"] for doc in documents]
    return url in urls


def get_info(url):
    documents = find_documents(db, collection_name)
    logging.info("Documents retrieved from MongoDB:")
    urls = [doc for doc in documents if doc["URL"] == url][0]
    return urls


def download_progress_hook(d):
    if d['status'] == 'downloading':
        logging.info(f"Downloading {d['filename']}: {d['_percent_str']} at {d['_speed_str']} ETA {d['_eta_str']}")
    elif d['status'] == 'finished':
        logging.info(f"Download complete: {d['filename']}")

def download_video(url, output_path='downloads'):
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'external_downloader': 'aria2c',
            'external_downloader_args': [
                '-j', '16',
                '-x', '16',  # Number of connections per server
                '-s', '16',  # Number of connections overall
                '-k', '5M'   # Piece size
            ],
            'playlistend': 100,  # Limit the number of videos to download to 100
            'writethumbnail': True,  # Download the thumbnail
            'progress_hooks': [download_progress_hook],
            
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logging.info(f"Video downloaded successfully from URL: {url}")
        return ydl_opts['outtmpl']
    except Exception as e:
        logging.error(f"Failed to download video from URL: {url}. Error: {e}")
        raise

def upload_progress(current, total):
    logging.info(f"Uploading: {current * 100 / total:.1f}%")

async def upload_video(app, chat_id, file_path, thumbnail_path):
    try:
        video = await app.send_video(chat_id, file_path, caption=file_path.split("/", 2)[-1], thumb=thumbnail_path, progress=upload_progress)
        logging.info(f"Video uploaded successfully to chat ID: {chat_id}")
        return video
    except Exception as e:
        logging.error(f"Failed to upload video to chat ID: {chat_id}. Error: {e}")
        raise

@app.on_message(filters.command("start"))
async def start_command(client, message):
    chat_id = message.chat.id
    await message.delete()
    welcome = await app.send_message(chat_id, "Send Any Yt-Dlp Supported Link to Download..")
    await asyncio.sleep(3)

@app.on_message(filters.command("speedtest"))
async def speedtest_command(client, message):
    chat_id = message.chat.id
    start = await app.send_message(chat_id, "<i>Initiating Speedtest...<i>")
    stats = get_speedtest_stats()
    caption = stats[1]
    photo = stats[0]
    await app.send_photo(chat_id, photo, caption)
    await start.delete()



@app.on_message(filters.command("stats"))
async def stats_command(client, message):
    chat_id = message.chat.id
    info = get_system_info()
    await app.send_message(chat_id,info)



    
@app.on_message(filters.text)
async def video(client, message):
    try:
        start_time = datetime.now()
        chat_id = message.chat.id
        if message.text.startswith("https://"):
            video_urls = [i.strip() for i in message.text.split()]
            await message.delete()
            video_hash = hash(video_urls[0])
            download_dir = f'downloads/{video_hash}'
            status = await app.send_message(chat_id,f"Processing {len(video_urls)} video(s) [{video_hash}]")
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            uploading = []
            for video_url in video_urls:
                if check_db(video_url):
                      data = get_info(video_url)
                      if chat_id != LINK_ID:
                          text = f"Sending Copy of {data['File_Name']} @ {chat_id}"
                          await app.send_message(LOG_ID,text,reply_to_message_id=data["PICID"])
                          await app.copy_message(chat_id,DUMP_ID,data["DMID"])
                else:
                    status = await status.edit_text(f"Processed {len(uploading)} Out Of {len(video_urls)}")
                    downloaded_video_path = download_video(video_url, output_path=download_dir)
                    exact_file_path = None
                    thumbnail_path = None
                    for root, dirs, files in os.walk(download_dir):
                        for file in files:
                            if file.endswith(('.mp4', '.mkv', '.webm')):
                                exact_file_path = os.path.join(root, file)
                            elif file.endswith(('.jpg', '.png', '.webp')):
                                thumbnail_path = os.path.join(root, file)
                            if exact_file_path and thumbnail_path and exact_file_path.split("/", 2)[-1] not in uploading:
                              uploading.append(exact_file_path.split("/", 2)[-1])
                              video = await upload_video(app, chat_id, exact_file_path, thumbnail_path)
                              if video:
                                     text = f"""
                                        <b>DMID:</b>{DM.id}\n\
                                        <b>DUMP_ID:</b>{DUMP_ID}\n\
                                        <b>URL:</b>{video_url}\n\
                                        <b>File_Name:</b>{exact_file_path.split("/", 2)[-1]}\n\
                                        <b>CHAT_ID:</b>{chat_id}\
                                    """
                                 PIC = await app.send_photo(LOG_ID,photo=thumbnail_path,caption=text)
                                 DM = await app.copy_message(DUMP_ID, video.chat.id,video.id,caption=f"""<b>File_Name:</b> <code>{exact_file_path.split("/", 2)[-1]}</code>\n<b>CHAT_ID:</b> <code>{chat_id}</code>""")
                                 result = {
                                    "DMID": DM.id,
                                    "PICID":PIC.id,
                                    "DUMP_ID": DUMP_ID,
                                    "URL": video_url,
                                    "File_Name": exact_file_path.split("/", 2)[-1],
                                    "CHAT_ID": chat_id,
                                 }
                                 insert_document(db, collection_nam.e, result)
                                 logging.info("Updated to Database!!")               
                                 os.remove(exact_file_path)
                                 os.remove(thumbnail_path)
                    else:
                        logging.error(f"Downloaded video or thumbnail file not found in '{download_dir}' directory.")
                await status.delete()
    except Exception as e:
        status = await send_message(LOG_ID,f"Error Occurred: {e}")
        logging.error(f"An error occurred: {e}")

print("Bot Started")
app.run()
