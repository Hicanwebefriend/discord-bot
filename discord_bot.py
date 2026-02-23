import os
import platform
import subprocess
import base64
import requests
import discord
import google.generativeai as genai
import yfinance as yf
import asyncio
from discord.ext import commands
from dotenv import load_dotenv


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stock(self, ctx, symbol: str = "SHB"):
        symbol = symbol.upper()
        
        lookup_symbol = f"{symbol}.VN" if len(symbol) == 3 and symbol.isalpha() else symbol
        
        async with ctx.typing():
            try:
                ticker = yf.Ticker(lookup_symbol)
                
                def fetch_data():
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        return hist['Close'].iloc[-1]
                    return None

                price = await asyncio.to_thread(fetch_data)
                
                if price is not None:
                    await ctx.send(f"📈 The latest closing price for **{symbol}** is: **{price:,.0f} VND**")
                else:
                    await ctx.send(f"❌ No data found for `{symbol}`. Please check if you typed it correctly!")
                    
            except Exception as e:
                await ctx.send(f"❌ An error occurred while fetching data: {e}")

    @commands.command(aliases=['gemini'])
    async def gemeni(self, ctx, *, prompt: str):
        async with ctx.typing():
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    await ctx.send("❌ Require GEMINI_API_KEY in file .env!")
                    return
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')            
                response = await model.generate_content_async(prompt)
                text = response.text
                if len(text) > 2000:
                    for i in range(0, len(text), 2000):
                        await ctx.send(text[i:i+2000])
                else:
                    await ctx.send(text)

            except Exception as e:
                await ctx.send(f"❌ Something went wrong while connecting: {e}")

    @commands.command()
    async def price(self, ctx, coin: str = "BTC"):
        symbol = f"{coin.upper()}USDT"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                price = float(data['price'])
                await ctx.send(f"📈 Current **{coin.upper()}** price is: **${price:,.2f}**")
            else:
                await ctx.send(f"❌ Cannot find `{symbol}`. Try another!")
                
        except Exception as e:
            await ctx.send(f"❌ Connection error with API: {e}")

    @commands.command()
    async def ping(self, ctx, host: str):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        
        try:
            result = subprocess.run(
                ['ping', param, '4', host],
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                await ctx.send(f"```\n{result.stdout}\n```")
            else:
                await ctx.send(f"❌ Could not reach {host}.\nError:\n```\n{result.stderr}\n```")
                
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def decode(self, ctx, *, encoded_text: str):
        try:
            decoded_bytes = base64.b64decode(encoded_text)
            decoded_string = decoded_bytes.decode('utf-8')
            await ctx.send(f"**✅ Decoded result:**\n```\n{decoded_string}\n```")
            
        except Exception:
            await ctx.send("❌ Error: Invalid Base64 string!")
    
    @commands.command(name="help")
    async def custom_help(self, ctx):
        embed = discord.Embed(
            title="🤖 SUCKBOT CONTROL PANEL",
            description="Here is the list of commands the bot can perform:",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="💰 `!price <coin_code>`", value="Check instant cryptocurrency prices (e.g., `!price btc`, `!price eth`)", inline=False)
        embed.add_field(name="📈 `!stock <symbol>`", value="Check stock prices (e.g., `!stock shb`, `!stock vic`)", inline=False)
        embed.add_field(name="🌐 `!ping <address>`", value="Check network connection (e.g., `!ping google.com`)", inline=False)
        embed.add_field(name="🔓 `!decode <string>`", value="Decode a Base64 string", inline=False)
        embed.add_field(name="🧠 `!gemeni <question>`", value="Summon Gemini AI to answer your questions (alias: `!gemini`)", inline=False)
        embed.add_field(name="🆘 `!help`", value="Show this help menu", inline=False)
        
        embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed)

class MyDiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.channel_id = 1440379955090554952

    async def setup_hook(self):
        await self.add_cog(UtilityCommands(self))

    async def on_ready(self):
        print(f"Bot online: {self.user}")
        channel = self.get_channel(self.channel_id)
        
        if channel is None:
            print("⚠ Channel not found. Please check your CHANNEL_ID or bot permissions.")
            return

        await channel.send("Bot has started running")

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    bot = MyDiscordBot()

    bot.run(TOKEN)