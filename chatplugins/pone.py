import io
import random

import requests

from bot import AbstractChatPlugin

event_id = 4

class ChatPlugin(AbstractChatPlugin):
    help = """/pony - присылает в ответ случайную картинку с поняшкой"""
    def call(self, event):
        if event[0] != event_id:
            return
        if event[6].partition(' ')[0] == '/pony':
            self.bot.vkapi.messages.setActivity(type='typing',peer_id=event[3])
            search_req = 'score.gt:200,safe,-animated,-svg,-comic'
            search_url = 'https://derpibooru.org/search.json'
            page_req = requests.get("{b}?q={s}".format(b=search_url, s=search_req), timeout=3)
            page_req.raise_for_status()
            total = page_req.json()['total']
            pages = -(-total // 15)
            page = random.randint(1, pages)
            req = requests.get("{b}?q={s}&page={p}".format(b=search_url, s=search_req, p=page), timeout=3)
            req.raise_for_status()
            random_img = random.choice(req.json()['search'])
            image_url = 'https:' + random_img['image']
            image_dbid = random_img['id']
            image_src = random_img['source_url']
            image_req = requests.get(image_url)
            image_req.raise_for_status()
            image = io.BytesIO(image_req.content)
            self.bot.vkapi.messages.setActivity(type='typing',peer_id=event[3])
            upload_server = self.bot.vkapi.photos.getMessagesUploadServer()
            upload_req = requests.post(upload_server['upload_url'],
                                       files={'photo': ('image.png', image, image_req.headers['content-type'])})
            upload_resp = self.bot.vkapi.photos.saveMessagesPhoto(**upload_req.json())

            image_vkid = upload_resp[0]['id']

            self.bot.vkapi.messages.send(message='http://derpibooru.org/' + str(image_dbid) + '\n' + image_src,
                                attachment='photo' + str(self.bot.bot_id) + '_' + str(image_vkid),
                                peer_id=event[3])
