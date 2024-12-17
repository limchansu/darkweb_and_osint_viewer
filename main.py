import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dw_crawler.htdark_crawler import htdark
from dw_crawler.island_crawler import island
from dw_crawler.leakbase_crawler import leakbase
from dw_crawler.lockbit_crawler import lockbit
from dw_crawler.play_crawler import play
from dw_crawler.rhysida_crawler import rhysida
from osint_crawler.github_crawler import github

async def setup_database(db_name, collection_names):

    client = AsyncIOMotorClient("mongodb://mongo1:30001,mongo2:30002,mongo:30003/?replicaSet=my-rs")
    db = client[db_name]

    existing_collections = await db.list_collection_names()
    for collection in collection_names:
        if collection not in existing_collections:
            await db.create_collection(collection)

    return db

async def exec_crawler():
    db_name = 'darkweb'
    collection_name = ['htdark', 'island', 'leakbase', 'lockbit', 'play', 'rhysida', 'github']
    db = await setup_database(db_name, collection_name)

    await asyncio.gather(
        htdark(db),
        island(db),
        leakbase(db),
        lockbit(db),
        play(db),
        rhysida(db),
        github(db)
    )

asyncio.run(exec_crawler())