import os
import logging
from pyrogram import Client,filters
from yt_dlp import YoutubeDL

# Configure logging
logging.basicConfig(
    filename='video_downloader.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Telegram API credentials
API_ID = '23080322'
API_HASH = 'b3611c291bf82d917637d61e4a136535'
BOT_TOKEN = '7199772252:AAHQfjo8VIWg2wDOCUXLdMt9klsQD_OuVx4'

# Create the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Progress hook for yt-dlp
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
                '-x', '16',  # Number of connections per server
                '-s', '16',  # Number of connections overall
                '-k', '1M'   # Piece size
            ],
            'playlistend': 100,  # Limit the number of videos to download to 100
            'writethumbnail': True,  # Download the thumbnail
            'progress_hooks': [download_progress_hook]
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
        await app.send_video(chat_id, file_path, thumb=thumbnail_path, progress=upload_progress)
        logging.info(f"Video uploaded successfully to chat ID: {chat_id}")
    except Exception as e:
        logging.error(f"Failed to upload video to chat ID: {chat_id}. Error: {e}")
        raise


@app.on_message(filters.private & filters.text)
async def video(client, message):
    chat_id = message.chat.id
    if message.text.startswith("https://"):
        await message.delete()
        status = await app.send_message(chat_id,"Video Is Processing")
        video_urls = [ i.strip()  for i in message.text.split()]       
        download_dir = 'downloads'
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        for video_url in video_urls:
            try:
                downloaded_video_path = download_video(video_url, output_path=download_dir)
                status = await status.edit_text("Video Has Been Downloaded..\nand Started To Upload")
                exact_file_path = None
                thumbnail_path = None
                for root, dirs, files in os.walk(download_dir):
                    for file in files:
                        if file.endswith(('.mp4', '.mkv', '.webm')):
                            exact_file_path = os.path.join(root, file)
                        elif file.endswith(('.jpg', '.png', '.webp')):
                            thumbnail_path = os.path.join(root, file)
                if exact_file_path and thumbnail_path:
                    #status = await status.edit_text("Video Starting to Upload..")
                    await upload_video(app, chat_id, exact_file_path, thumbnail_path)
                    await status.delete()
                else:
                    logging.error(f"Downloaded video or thumbnail file not found in '{download_dir}' directory.")
                    #status = await status.edit_text(f"Downloaded video or thumbnail file not found in '{download_dir}' directory.")
                    
            except Exception as e:
                status = await status.edit_text(f"Error Occured:{e}")
                logging.error(f"An error occurred: {e}")

print("Bot Started")
app.run()
