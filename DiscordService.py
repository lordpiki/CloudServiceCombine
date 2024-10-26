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
                    await self.download(task['file_id'], 1, task['file_name'])
                        
        bot.run(token)    
               
    async def upload(self, file_path, file_id):
        try:
            channel_id = os.getenv('DISCORD_CHANNEL_ID')
            chat = self.client.get_channel(int(channel_id))
            
            chunks = FileHandler.break_down_file(file_path, self.max_file_size)
            attachments = []
            for chunk in chunks:
                attachments.append(discord.File(io.BytesIO(chunk), filename=f"{file_id}_{len(attachments)}"))
            await chat.send(files=attachments)
                
        except Exception as e:
            print(e)
            
    async def download(self, file_id, chunk_count, file_path):
        try:
            channel_id = os.getenv('DISCORD_CHANNEL_ID')
            chat = self.client.get_channel(int(channel_id))
            all_chunks = []
            async for message in chat.history(limit=None):
                if len(all_chunks) >= chunk_count:
                    break
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.filename.startswith(file_id):
                            all_chunks.append(attachment)
            all_chunks.sort(key=lambda x: int(x.filename.split('_')[1]))
                                        
        except Exception as e:
            print(e)
               