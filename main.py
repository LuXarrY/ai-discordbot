import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
import time
import asyncio

# Load environment variables
load_dotenv(".env")

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
chat_model = genai.GenerativeModel('models/gemini-2.0-flash')

class LuXBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            application_id=os.getenv('BOTUN_IDSİ')
        )

        self.last_message_time = {}
        self.timeout_duration = 2
        self.allowed_channels = [KANALIDGİR, AYNIGİREBİLİRSİN]

    async def setup_hook(self):
        print("🔄 Komutlar senkronize ediliyor...")
        try:
            synced = await self.tree.sync()
            print(f"✅ {len(synced)} komutu senkronize edildi")
        except Exception as e:
            print(f"❌ Komutlar senkronize edilemedi: {str(e)}")

    async def on_ready(self):
        print(f"✅ {self.user} is ready!")
        print(f"🌐 Bot Toplam {len(self.guilds)} Sunucuda")
        print(f"🔗 Davet URL: https://discord.com/api/oauth2/authorize?client_id={self.application_id}&permissions=8&scope=bot%20applications.commands")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="LuX <3"
            )
        )

    async def on_message(self, message):
        if message.author == self.user or message.channel.id not in self.allowed_channels:
            return

        # Timeout kontrolü
        current_time = time.time()
        last_time = self.last_message_time.get(message.author.id, 0)
        if current_time - last_time < self.timeout_duration:
            remaining = round(self.timeout_duration - (current_time - last_time), 1)
            await message.reply(f"⏳ Yavaş biraz, {remaining} saniye bekle.")
            return

        self.last_message_time[message.author.id] = current_time

        try:
            async with message.channel.typing():
                prompt = f"""Sen Türkçe konuşan, samimi ve mizahi cevaplar veren bir yapay zekasın. Kullanıcının mesajına kısa, net ve eğlenceli bir cevap ver. Küfür etme, romantik olma, resmi konuşma. Sokak ağzı kullanabilirsin ama saygı çerçevesinde.\n\nKullanıcının mesajı: {message.content}\n\nCevabın:"""
                response = await chat_model.generate_content_async(prompt)
                await message.reply(response.text.strip())
        except Exception as e:
            if "429" in str(e):
                await message.reply("❌ Limitim dolmuş olabilir, birazdan tekrar dene.")
            else:
                await message.reply(f"❌ Hata oluştu: {e}")

bot = LuXBot()
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError("❌ DISCORD_TOKEN token ayarlı değil ?")

try:
    bot.run(token)
except discord.errors.LoginFailure:
    print("❌ Geçersiz token!")
except Exception as e:
    print(f"❌ Başka bir hata oluştu: {e}")
