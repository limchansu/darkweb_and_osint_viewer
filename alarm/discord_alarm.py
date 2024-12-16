import asyncio
import pytz
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient


# MongoDB 연결 설정
client = AsyncIOMotorClient("mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-rs")

TOKEN = ''

# 필요한 intents 설정
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='!', intents=intents)
# 채널 ID 설정
DARKWEB_CHANNEL_ID = 1317725156386410619  # 다크웹 채널 아이디
OSINT_CHANNEL_ID = 1318099564116578305 # 오신트 채널 아이디

async def darkweb_monitor(db):
    pipeline = [{"$match": {"operationType": "insert"}}]

    try:
        # 비동기 컨텍스트 매니저 사용
        async with db.watch(pipeline=pipeline) as stream:
            print("darweb 데이터베이스 모니터링 중")
            async for change in stream:
                # Change Stream 이벤트 처리
                new_document = change.get("fullDocument")
                print("데이터 추가 됨 :", new_document)
                site_name = change.get("ns").get("coll")
                timestamp = new_document["_id"].generation_time
                local_timezone = pytz.timezone("Asia/Seoul")
                local_timestamp = timestamp.astimezone(local_timezone)
                channel = bot.get_channel(DARKWEB_CHANNEL_ID)
                if channel:
                    await channel.send(f"📢 **다크웹에서 유출된 정보 감지**\n**제목**: {new_document.get('title', '제목 없음')}\n**유출한 사이트** : {site_name}\n**UTC 시간**: {timestamp}\n**한국 시간**: {local_timestamp}")
                else:
                    print("채널을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        await asyncio.sleep(5)

async def osint_monitor(db):
    pipeline = [{"$match": {"operationType": "insert"}}]

    try:
        # 비동기 컨텍스트 매니저 사용
        async with db.watch(pipeline=pipeline) as stream:
            print("OSINT 데이터베이스 모니터링 중")
            async for change in stream:
                # Change Stream 이벤트 처리
                new_document = change.get("fullDocument")
                print("데이터 추가 됨 :", new_document)
                site_name = change.get("ns").get("coll")
                timestamp = new_document["_id"].generation_time
                local_timezone = pytz.timezone("Asia/Seoul")
                local_timestamp = timestamp.astimezone(local_timezone)
                channel = bot.get_channel(DARKWEB_CHANNEL_ID)
                if channel:
                    await channel.send(
                        f"📢 **OSINT 정보 감지**\n**제목**: {new_document.get('title', '제목 없음')}\n**사이트** : {site_name}\n**UTC 시간**: {timestamp}\n**한국 시간**: {local_timestamp}")
                else:
                    print("채널을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        await asyncio.sleep(5)

# 봇 실행
def discord_agent():
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
        asyncio.create_task(darkweb_monitor(client['web_crawler']))
        asyncio.create_task(osint_monitor(client['osint']))

    bot.run(TOKEN)

