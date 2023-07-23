from threads_api.src.threads_api import ThreadsAPI
import asyncio
# from threads_api.src.http_sessions.instagrapi_session import InstagrapiSession
# from threads_api.src.http_sessions.requests_session import RequestsSession
# from threads_api.src.http_sessions.aiohttp_session import AioHTTPSession
import base64
import json
from Quote2Image import Convert, GenerateColors
from pprint import pprint
import platform
from threads import Threads
import time
import os
from dotenv import load_dotenv

load_dotenv()


def genQuote(text,author, img_name):
    fg = '#fff'
    bg = '#000'

    img = Convert(
        quote=text,
        author=author,
        fg=fg,
        bg=bg,
        font_size=32,
        font_type="fonts/Kalam-Bold.ttf",
        font_size_author=25,
        width=1080,
        height=450,
        watermark_text="@i_miss_her_bot",
        watermark_font_size=15
    )

    img.save(img_name + ".png")
    
def getDest(data_string):
    start_index = data_string.find('=') + 1
    end_index = data_string.find('_')
    result = data_string[start_index:end_index]
    
    return result

async def post_include_image(api, parent_id, img):
    result = await api.post("This thread has been generated as quote image !", parent_post_id=parent_id, image_path=img)
    print(f"Post has been successfully !")

async def get_notifications(api : ThreadsAPI):
    res = await api.get_notifications()

    return res

def append_to_file(file_path, data):
    try:
        with open(file_path, 'a') as file:
            file.write(data + '\n')
        print("Data appended successfully.")
    except IOError:
        print("Error: Unable to append data to the file.")
        
def check_value_in_file(file_path, value):
    try:
        # Open the file for reading
        with open(file_path, 'r') as file:
            # Read all lines and store them in a list
            lines = file.readlines()

            # Check if the value is in any of the lines (assuming one value per line)
            for line in lines:
                if line.strip() == str(value):
                    return True

        # If the value is not found in any of the lines, return False
        return False

    except IOError:
        print("Error: Unable to read the file.")
        return False
        
async def main():
    api = ThreadsAPI()
    threads = Threads()
    # Will login via REST to the Instagram API
    is_success = await api.login(username=os.getenv('TH_USERNAME'), password=os.getenv('TH_PASSWORD'), cached_token_path=".token")
    print(f"Login status: {'Success' if is_success else 'Failed'}")

    if is_success:
        notifs = await get_notifications(api) # Get a list of notifications
        merged_stories = notifs['old_stories'] + notifs['new_stories']
        matching_stories = [story for story in merged_stories if story.get('type') == 20]

        r = json.dumps(matching_stories)
        loaded_r = json.loads(r)
        
        for data in loaded_r:
            parent_id = getDest(data['args']['destination'])
            # res = await get_post(api)
            res = threads.public_api.get_thread(id=parent_id)
            threadData = res['data']['data']['containing_thread']['thread_items'][0]['post']
            caption = threadData['caption']
            if caption is not None:
                txt = caption['text']
                author = threadData['user']['username']
                
                img_name = str(time.time())
                if check_value_in_file("reply.log", parent_id) is False:
                    genQuote(txt, author, img_name)
                    await post_include_image(api, parent_id, img_name+".png")
                    append_to_file("reply.log", parent_id)
            # print(response)
        
    await api.close_gracefully()

if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

counter = 1
while True:
    asyncio.run(main())
    counter += 1
    time.sleep(3)  # Delay for 3 seconds between each iteration
    print(counter)