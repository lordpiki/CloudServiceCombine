import io
from Service import Service
from FileHandler import FileHandler
from dotenv import load_dotenv  
import discord
from discord.ext import commands
import os
import threading

class DiscordService(Service):
    
    def __init__ (self, tasks):
        MB25 = 25 * 1024 * 1024
        super().__init__(float('inf'), MB25)
        
        load_dotenv()
        self.task_stack = tasks
        self.thread = threading.Thread(target=self.create_bot)
        self.thread.start()
        
    def create_bot(self):
        
        intents = discord.Intents.default()
        intents.message_content = False
        bot = commands.Bot(command_prefix='!', intents=intents)

        token = os.getenv('DISCORD_BOT_SECRET')
        self.client = bot
        
        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user}')            
            for task in self.task_stack:
                if task['type'] == 'upload':
                    await self.upload(task['file_path'], task['file_id'])
                elif task['type'] == 'download':
                    await self.download(task['file_id'])
                        
        bot.run(token)    
               
    async def upload(self, file_path, file_id):
        try:
            channel_id = os.getenv('DISCORD_CHANNEL_ID')
            chat = self.client.get_channel(int(channel_id))
            
            chunks = FileHandler.break_down_file(file_path, self.max_file_size)
            chunk_count = 0
            for chunk in chunks:
                print(f"Uploading chunk {chunk_count}")
                await chat.send(file=discord.File(io.BytesIO(chunk),filename=f"{file_id}_{chunk_count}"))
                
        except Exception as e:
            print(e)
            
    async def download(self, file_id, chunk_count):
        try:
            channel_id = os.getenv('DISCORD_CHANNEL_ID')
            chat = self.client.get_channel(int(channel_id))
            async for message in chat.history(limit=200):
                if message.attachments:
                    attachment = message.attachments[0]
                    if attachment.id == file_id:
                        await attachment.save(attachment.filename)
                        break
        except Exception as e:
            print(e)
               