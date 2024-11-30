import io
from Service import Service
from FileHandler import FileHandler
import discord
from discord.ext import commands
import os
import threading
import uuid
import requests

class DiscordService(Service):
    
    def __init__ (self, credentials:dict, name: str):
        MB25 = 25 * 1024 * 1024
        super().__init__(max_storage=float('inf'), max_file_size=MB25, name=name)
        self.token = credentials['token']
        self.channel_id = credentials['channel_id']
        
    def create_bot(self,parts):
        print('Creating bot')
        intents = discord.Intents.default()
        intents.message_content = False
        bot = commands.Bot(command_prefix='!', intents=intents)
        self.client = bot
        
        @bot.event
        async def on_ready():
            self.parts_ids = await self.upload_parts(parts) 
            print('Bot is ready')
            await bot.close()
                     
        bot.run(self.token)    
        print('Bot closed')
        
    def upload(self, parts: list) -> list[str]:
        thread = threading.Thread(target=self.create_bot, args=(parts,))
        thread.start()
        thread.join()
        return self.parts_ids
               
    async def upload_parts(self, parts):
        try:
            chat = self.client.get_channel(int(self.channel_id))
            parts_ids = []
            
            for part in parts:
                discord_file = discord.File(io.BytesIO(part[0]), filename=part[1])
                message = await chat.send(file=discord_file)
                attachment = message.attachments[0]
                parts_ids.append(attachment.url)
            
            return parts_ids
                
        except Exception as e:
            print(e)
    
    def download(self, parts_ids: list[str]) -> list:
        try:
            parts = []
            for part_id in parts_ids:
                response = requests.get(part_id)
                parts.append(response.content)
            return parts
        except Exception as e:
            print(e)
            
    
    # async def download(self, file_id, chunk_count, file_path):
    #     try:
    #         channel_id = os.getenv('DISCORD_CHANNEL_ID')
    #         chat = self.client.get_channel(int(channel_id))
    #         all_chunks = []
    #         async for message in chat.history(limit=None):
    #             if len(all_chunks) >= chunk_count:
    #                 break
    #             if message.attachments:
    #                 for attachment in message.attachments:
    #                     if attachment.filename.startswith(file_id):
    #                         all_chunks.append(attachment)
    #         all_chunks.sort(key=lambda x: int(x.filename.split('_')[1]))
                                        
    #     except Exception as e:
    #         print(e)
               
