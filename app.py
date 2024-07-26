import os
import logging
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
import static_ffmpeg
import asyncio 
from datetime import datetime
import time
from speed import *
from alive import keep_alive 
from config import *
from database import *



database_name = "Spidydb"
db = connect_to_mongodb(DATABASE, database_name)
collection_name = "PHVDL"

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
     urls = [ doc["URL"] for doc in documents]
     if url in urls:
       return True
     else:
         return False



    

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
        await app.send_video(chat_id, file_path, caption=file_path.split("/", 2)[-1], thumb=thumbnail_path, progress=upload_progress)
        logging.info(f"Video uploaded successfully to chat ID: {chat_id}")
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




@app.on_message(filters.text)
async def video(client, message):
    start_time = datetime.now()
    chat_id = message.chat.id
    user_mention = message.from_user.mention
    if message.text.startswith("https://"):
        await message.delete()
        video_urls = [i.strip() for i in message.text.split()]
        video_hash = hash(video_urls[0])
        download_dir = f'downloads/{video_hash}'
        status = await app.send_message(chat_id, f"Video Is Processing [{video_hash}]")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        uploading = []
        for video_url in video_urls:
            try: 
              if not check_db(video_url):
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
                            LM = await video.forward(LOG_ID)
                            await LM.edit_caption(f"""<b>File_Name:<b> <code>{exact_file_path}<code>\n<b>User:<b> <code>{user_mention}<code>""")
                            result = {"LMID":LM.id,"LOG_ID":LOG_ID,"URL":video_url,"File_Name":exact_file_path,"CHAT_ID":chat_id,}
                            insert_document(db, collection_name, result)
                            logging.info("Updated to Database!!")               
                            await status.delete()
                            os.remove(exact_file_path)
                            os.remove(thumbnail_path)
                else:
                    logging.error(f"Downloaded video or thumbnail file not found in '{download_dir}' directory.")
            except Exception as e:
                status = await status.edit_text(f"Error Occurred: {e}")
                logging.error(f"An error occurred: {e}")





app.run()
