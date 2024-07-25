import speedtest
from speedtest import ConfigRetrievalError
import aiohttp
import asyncio
import logging

LOGGER = logging.getLogger(__name__)

async def get_readable_file_size(size):
    return f"{size / (1024 ** 2):.2f} MB"

async def send_message(message, content, photo=None):
    print(content)
    return content

async def edit_message(message, new_content):
    print(new_content)

async def delete_message(message):
    pass

async def speedtest(app, message):
    speed = await app.send_message(message.chat.id, "<i>Initiating Speedtest...</i>")
    try:
        test = speedtest.Speedtest()
    except ConfigRetrievalError:
        await speed.edit_text("<b>ERROR:</b> <i>Can't connect to Server at the Moment, Try Again Later !</i>")
        return

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    path = result['share']

    string_speed = f'''
➲ <b><i>SPEEDTEST INFO</i></b>
┠ <b>Upload:</b> <code>{await get_readable_file_size(result['upload'] / 8)}/s</code>
┠ <b>Download:</b> <code>{await get_readable_file_size(result['download'] / 8)}/s</code>
┠ <b>Ping:</b> <code>{result['ping']} ms</code>
┠ <b>Time:</b> <code>{result['timestamp']}</code>
┠ <b>Data Sent:</b> <code>{await get_readable_file_size(int(result['bytes_sent']))}</code>
┖ <b>Data Received:</b> <code>{await get_readable_file_size(int(result['bytes_received']))}</code>

➲ <b><i>SPEEDTEST SERVER</i></b>
┠ <b>Name:</b> <code>{result['server']['name']}</code>
┠ <b>Country:</b> <code>{result['server']['country']}, {result['server']['cc']}</code>
┠ <b>Sponsor:</b> <code>{result['server']['sponsor']}</code>
┠ <b>Latency:</b> <code>{result['server']['latency']}</code>
┠ <b>Latitude:</b> <code>{result['server']['lat']}</code>
┖ <b>Longitude:</b> <code>{result['server']['lon']}</code>

➲ <b><i>CLIENT DETAILS</i></b>
┠ <b>IP Address:</b> <code>{result['client']['ip']}</code>
┠ <b>Latitude:</b> <code>{result['client']['lat']}</code>
┠ <b>Longitude:</b> <code>{result['client']['lon']}</code>
┠ <b>Country:</b> <code>{result['client']['country']}</code>
┠ <b>ISP:</b> <code>{result['client']['isp']}</code>
┖ <b>ISP Rating:</b> <code>{result['client']['isprating']}</code>
'''
    try:
        pho = await app.send_photo(message.chat.id, photo=path,caption= string_speed)
        await delete_message(speed)
    except Exception as e:
        LOGGER.error(str(e))
        await message.edit_text(speed, string_speed)
