import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dw_crawler.abyss_crawler import abyss
from dw_crawler.blackbasta_crawler import blackbasta
from dw_crawler.blacksuit_crawler import blacksuit
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
    darkweb_collection_name = ['abyss','blackbasta','ctifeeds','daixin','darknetARMY', 'htdark', 'island', 'leakbase', 'lockbit', 'play', 'rhysida']
    darweb_db = await setup_database('darkweb', darkweb_collection_name)
    osint_collection_name = ['github', 'tuts4you', 'x00org']
    osint_db = await setup_database('osint', osint_collection_name)

    await asyncio.gather(
        abyss(darweb_db),
        # blackbasta(darweb_db),
        # blacksuit(darweb_db),
        # htdark(darweb_db),
        # island(darweb_db),
        # leakbase(darweb_db),
        # lockbit(darweb_db),
        # play(darweb_db),
        # rhysida(darweb_db),
        # github(osint_db)
    )

asyncio.run(exec_crawler())