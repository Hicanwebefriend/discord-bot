import os
import platform
import subprocess
import base64
import requests
import discord
import google.generativeai as genai
from discord.ext import commands
from dotenv import load_dotenv


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['gemini'])
    async def gemeni(self, ctx, *, prompt: str):
        async with ctx.typing():
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    await ctx.send("❌ Thiếu cấu hình GEMINI_API_KEY trong file .env!")
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
                await ctx.send(f"❌ Có lỗi xảy ra khi kết nối với não bộ: {e}")
    @commands.command()
    async def price(self, ctx, coin: str = "BTC"):
        symbol = f"{coin.upper()}USDT"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                price = float(data['price'])
                await ctx.send(f"📈 Giá **{coin.upper()}** hiện tại đang là: **${price:,.2f}**")
            else:
                await ctx.send(f"❌ Không tìm thấy cặp giao dịch `{symbol}`. Bạn thử lại mã khác nhé!")
                
        except Exception as e:
            await ctx.send(f"❌ Có lỗi mạng hoặc API: {e}")

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
            await ctx.send(f"**✅ Kết quả giải mã:**\n```\n{decoded_string}\n```")
            
        except Exception:
            await ctx.send("❌ Lỗi: Chuỗi Base64 không hợp lệ!")
    
    @commands.command(name="help")
    async def custom_help(self, ctx):
        embed = discord.Embed(
            title="🤖 BẢNG ĐIỀU KHIỂN SUCKBOT",
            description="Dưới đây là danh sách các lệnh thần thánh mà bot có thể làm được:",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="💰 `!price <mã_coin>`", value="Tra cứu giá tiền ảo tức thời (VD: `!price btc`, `!price eth`)", inline=False)
        embed.add_field(name="🌐 `!ping <địa_chỉ>`", value="Kiểm tra kết nối mạng (VD: `!ping google.com`)", inline=False)
        embed.add_field(name="🔓 `!decode <chuỗi>`", value="Giải mã chuỗi Base64 bí ẩn", inline=False)
        embed.add_field(name="🧠 `!gemeni <câu_hỏi>`", value="Triệu hồi AI Gemini giải đáp mọi thắc mắc (alias: `!gemini`)", inline=False)
        embed.add_field(name="🆘 `!help`", value="Hiển thị bảng hướng dẫn này", inline=False)
        
        embed.set_footer(text=f"Người dùng yêu cầu: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
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
            print("⚠ Không tìm thấy channel. Kiểm tra lại CHANNEL_ID hoặc quyền của bot.")
            return

        await channel.send("Bot has started running")

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    bot = MyDiscordBot()
    bot.run(TOKEN)