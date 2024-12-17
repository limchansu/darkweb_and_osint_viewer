from quart import Quart, request, jsonify, render_template
from quart_cors import cors  # Quart 용 CORS
import asyncio
import sys, os
from motor.motor_asyncio import AsyncIOMotorClient  # motor를 사용하여 비동기 MongoDB 클라이언트 사용

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from main import setup_database, run_crawling


app = Quart(__name__)
app = cors(app)  # 모든 도메인에 대해 CORS 허용

# 전역 변수로 데이터베이스 연결 유지
dw_db = None
osint_db = None

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/search', methods=['POST'])
async def search():
    # 요청 파라미터
    data = await request.get_json()  # JSON 데이터 비동기 파싱

    keywords = data.get('keywords', '').strip()  # 검색어
    category = data.get('category', '')
    option = data.get('option', '')

    # 초기화
    db_collection = None
    results = []

    # 컬렉션 선택
    if category == "osint":
        db_collection = osint_db[option]
    elif category == "darkweb":
        db_collection = dw_db[option]
    else:
        return jsonify({"error": "Invalid collection"}), 400

    # 검색어가 있을 경우 제목에서 검색
    if keywords:
        search_filter = {"title": {"$regex": keywords, "$options": "i"}}  # 대소문자 구분 없는 검색
        cursor = db_collection.find(search_filter)
    else:
        cursor = db_collection.find()

    # 비동기적으로 모든 결과를 가져오기
    docs = []
    async for doc in cursor:
        docs.append(doc)  # cursor에서 비동기적으로 문서를 순회하며 docs에 추가

    # DB 탐색 결과 가공
    for doc in docs:
        result = {
            "_id": str(doc.get("_id")),  # ObjectId를 문자열로 변환
            "title": doc.get("title"),
            "url": doc.get("url"),
            "keyword": doc.get("keyword", "")  # 필요한 다른 필드도 추가 가능
        }
        results.append(result)

    return jsonify({
        "results": results
    })

async def initialize_and_run_crawling():
    """
    데이터베이스 초기화 및 크롤링 실행 (비동기)
    """
    global dw_db, osint_db

    # 데이터베이스 생성 및 연결
    dw_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                      "daixin", "darkleak", "darknetARMY", "everest", "island",
                      "leakbase", "lockbit", "play", "rhysida", "htdark"]
    dw_db = setup_database("darkweb", dw_collections)

    osint_collections = ["github", "tuts4you", "0x00org"]
    osint_db = setup_database("osint", osint_collections)

    # 비동기 크롤링 시작
    print("Starting crawling...")
    await asyncio.to_thread(run_crawling)  # run_crawling을 비동기로 실행

# Quart 애플리케이션 시작 시 크롤링 실행
@app.before_serving
async def startup_tasks():
    """
    서버 시작 시 초기화 작업 수행
    """
    asyncio.create_task(initialize_and_run_crawling())

if __name__ == '__main__':
    app.run(debug=True)
