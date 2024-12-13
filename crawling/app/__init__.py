from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 6))
    search_type = request.args.get('searchType', 'osint')  # 'osint' 또는 'darkweb' 값
    
    # 예시 데이터 - 실제로는 검색 옵션에 따라 다른 데이터를 반환
    if search_type == 'osint':
        results = [{"title": f"OSINT Card {i}", "subtitle": f"OSINT Subtitle {i}", "description": f"OSINT Description {i}", "link": "#"} for i in range((page - 1) * limit + 1, page * limit + 1)]
    else:
        results = [{"title": f"Darkweb Card {i}", "subtitle": f"Darkweb Subtitle {i}", "description": f"Darkweb Description {i}", "link": "#"} for i in range((page - 1) * limit + 1, page * limit + 1)]

    total_results = 50  # 예시로 50개의 결과
    total_pages = (total_results + limit - 1) // limit  # 페이지 수 계산
    return jsonify({"results": results, "totalPages": total_pages})

if __name__ == '__main__':
    app.run(debug=True)
