import asyncio

import discord
from discord.ext import commands
from pymongo import MongoClient

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017/")
db = client["your_database_name"]
collection = db["your_collection_name"]

TOKEN = ''

# 필요한 intents 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 접근

# 봇 초기화
bot = commands.Bot(command_prefix='!', intents=intents)
# 채널 ID 설정
CHANNEL_ID = 1317725156386410619  # 알림을 보낼 채널의 ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # MongoDB Change Stream 감지 루프 시작
    asyncio.create_task(monitor_database())


async def monitor_database():
    """MongoDB Change Stream으로 데이터 추가 이벤트 감지"""
    pipeline = [{"$match": {"operationType": "insert"}}]  # Insert 이벤트만 필터링

    with collection.watch(pipeline=pipeline) as stream:
        print("MongoDB 데이터 변경 감지 중...")
        for change in stream:
            # 새로 추가된 데이터 가져오기
            new_document = change["fullDocument"]
            print("새 데이터 추가 감지:", new_document)

            # Discord 채널로 알림 보내기
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                message = f"새 데이터가 추가되었습니다: {new_document}"
                await channel.send(message)
            else:
                print("채널을 찾을 수 없습니다.")

# 봇 실행
bot.run(TOKEN)