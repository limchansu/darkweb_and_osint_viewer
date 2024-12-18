from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from main import setup_database, run_crawler_periodically
import asyncio
import threading
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# 전역 변수
dw_db = None
osint_db = None

def initialize_databases():
    """동기적 데이터베이스 초기화"""
    global dw_db, osint_db
    
    print("Initializing databases...")
    client = MongoClient("mongodb://localhost:27017/")
    
    dw_db = client['darkweb']
    osint_db = client['osint']
    
    # 컬렉션 생성
    dw_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                    "daixin", "darkleak", "darknetARMY", "everest", "island",
                    "leakbase", "lockbit", "play", "rhysida", "htdark"]
    
    osint_collections = ["github", "tuts4you", "0x00org"]
    
    for collection in dw_collections:
        if collection not in dw_db.list_collection_names():
            dw_db.create_collection(collection)
    
    for collection in osint_collections:
        if collection not in osint_db.list_collection_names():
            osint_db.create_collection(collection)
    
    print("Database initialization completed")

def run_async_crawler():
    """비동기 크롤러를 별도의 이벤트 루프에서 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_crawler_periodically())
    loop.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    keywords = data.get('keywords', '').strip()
    category = data.get('category', '')
    option = data.get('option', '')

    if category == "osint":
        db_collection = osint_db[option]
    elif category == "darkweb":
        db_collection = dw_db[option]
    else:
        return jsonify({"error": "Invalid collection"}), 400

    search_filter = {"title": {"$regex": keywords, "$options": "i"}} if keywords else {}
    cursor = db_collection.find(search_filter)
    
    results = [{
        "_id": str(doc.get("_id")),
        "title": doc.get("title"),
        "url": doc.get("url"),
        "keyword": doc.get("keyword", "")
    } for doc in cursor]

    return jsonify({"results": results})

if __name__ == '__main__':
    # 데이터베이스 초기화 (동기적)
    initialize_databases()
    
    # 크롤러 스레드 시작
    crawler_thread = threading.Thread(target=run_async_crawler, daemon=True)
    crawler_thread.start()
    
    # Flask 앱 실행
    app.run(debug=False, use_reloader=False)