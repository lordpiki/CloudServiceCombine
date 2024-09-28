import io
from Service import Service
from FileHandler import FileHandler
from dotenv import load_dotenv  
import discord
from discord.ext import commands
import os
import threading

class DiscordService(Service):
    
    def __init__ (self):
        MB25 = 25 * 1024 * 1024
        super().__init__(float('inf'), MB25)
        
        load_dotenv()
        self.bot_ready = False
        self.task_stack = []
        

        
    def is_ready(self):
        return self.bot_ready

    def create_task(self, task):
        self.task_stack.append(task)
        
    def create_bot(self):
        
        intents = discord.Intents.default()
        intents.message_content = False
        bot = commands.Bot(command_prefix='!', intents=intents)

        token = os.getenv('DISCORD_BOT_SECRET')
        self.client = bot
        
        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user}')
            self.bot_ready = True
            
            while True:
                if len(self.task_stack) > 0:
                    task = self.task_stack.pop()
                    if task['type'] == 'upload':
                        await self.upload(task['file_path'])
                    elif task['type'] == 'download':
                        await self.download(task['file_id'])
                        
        bot.run(token)    
               
    async def upload(self, file_path):
        try:
            chunks = FileHandler.break_down_file(file_path, self.max_file_size)
            channel_id = os.getenv('DISCORD_CHANNEL_ID')
            print(channel_id, flush=True)
            chat = self.client.get_channel(int(channel_id))
            print(chat, flush=True)
            for chunk in chunks:
                await chat.send(file=discord.File(io.BytesIO(chunk),filename="test.png"))
        except Exception as e:
            print(e)
            
    async def download(self, file_id):
        pass
               
        
if __name__ == '__main__':
    service = DiscordService()
    thread = threading.Thread(target=service.create_bot)
    thread.start()
    service.create_task({'type': 'upload', 'file_path': 'test.png'}) 
    thread.join()