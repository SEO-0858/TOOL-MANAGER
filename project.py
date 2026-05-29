import sys
from pymongo import MongoClient

# 💡 dnspython 패키지가 정상적으로 로드되는지 먼저 확인
print("1. [패키지 검사] dnspython 라이브러리 확인 중...")
try:
    import dns.resolver
    print("   ✅ dnspython 패키지가 정상적으로 설치되어 있습니다.")
except ImportError:
    print("   ❌ 에러: dnspython 패키지가 없습니다. 'pip install dnspython'을 실행하세요.")
    sys.exit(1)

# =================================================================
# 🔌 [MongoDB Atlas 연결 설정] - 회원님의 실제 주소
# =================================================================
MONGO_URI = "mongodb+srv://sspon1270_db_user:wXA7NGCMjjTiTG5w@cluster0.lectnsv.mongodb.net/tool_manager?appName=Cluster0"

print("\n2. [DB 접속 시도] MongoDB Atlas 서버에 연결을 시도합니다...")
try:
    # 제한 시간(timeout)을 5초로 설정하여 무한 대기를 방지합니다.
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # 핑(Ping) 테스트를 날려 응답이 오는지 확인합니다.
    client.admin.command('ping')
    print("   ✅ 서버 응답 확인! 물리적인 네트워크 연결에 성공했습니다.")
    
    # 데이터베이스와 컬렉션 선택
    db = client["tool_manager"]
    collection = db["test_connection"]
    
    print("\n3. [데이터 쓰기/읽기 테스트] 가짜 데이터를 넣고 빼봅니다...")
    
    # 임시 데이터 1건 저장 테스트
    test_data = {"status": "success", "message": "연결 테스트 성공!"}
    insert_result = collection.insert_one(test_data)
    print(f"   ✅ 데이터 쓰기 성공! (생성된 문서 ID: {insert_result.inserted_id})")
    
    # 방금 넣은 데이터 다시 찾아오기 테스트
    find_data = collection.find_one({"_id": insert_result.inserted_id})
    print(f"   ✅ 데이터 읽기 성공! (가져온 메시지: {find_data['message']})")
    
    # 테스트로 만든 임시 데이터 삭제 청소
    collection.delete_one({"_id": insert_result.inserted_id})
    print("   ✅ 테스트 데이터 정리 완료.")
    
    print("\n🎉 [최종 결과] 데이터베이스가 100% 정상 작동하며, 네트워크가 완벽히 뚫려있습니다!")

except Exception as e:
    print("\n💥 [연결 실패] 에러가 발생했습니다. 아래 메시지를 분석하세요:")
    print("-" * 60)
    print(e)
    print("-" * 60)
    print("\n💡 조치 팁:")
    if "DNS" in str(e) or "Configuration" in str(e):
        print("👉 여전히 DNS 에러가 난다면, 현재 컴퓨터의 인터넷 공유기나 통신사 망이 'mongodb+srv' 주소를 지원하지 않는 것입니다.\n   [해결법] 컴퓨터 인터넷을 '스마트폰 핫스팟'으로 변경하고 다시 실행해 보세요.")
    else:
        print("👉 방화벽 문제이거나 ID/PW 오류일 수 있습니다. MongoDB 웹사이트에서 비밀번호를 재발급받아 보세요.")

