import sys
from pymongo import MongoClient

# 1. 연결 주소 설정 (회원님 정보)
MONGO_URI = "mongodb+srv://sspon1270_db_user:wXA7NGCMjjTiTG5w@cluster0.lectnsv.mongodb.net/tool_manager?appName=Cluster0"

print("🔄 몽고DB 연결 테스트를 시작합니다...")

try:
    # 2. 클라이언트 생성 (연결 시도 제한시간을 5초로 설정)
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # 3. 핑(Ping) 명령을 날려 실제 서버 응답이 오는지 확인
    # 여기서 막히면 네트워크나 DNS 문제입니다.
    client.admin.command('ping')
    print("📬 [1단계] 서버 응답(Ping) 성공! 네트워크가 연결되어 있습니다.")
    
    # 4. 가짜 데이터를 하나 찔러넣어서 읽고 쓰기가 되는지 확인
    db = client["tool_manager"]
    collection = db["test_connection"]
    
    # 임시 데이터 삽입
    res = collection.insert_one({"test": "hello"})
    print("📝 [2단계] 데이터 쓰기 성공!")
    
    # 임시 데이터 삭제 (흔적 지우기)
    collection.delete_one({"_id": res.inserted_id})
    print("🧹 [3단계] 테스트 데이터 정리 완료!")
    
    print("\n🎉 [최종 결과] 연결 대성공! 데이터베이스가 완벽하게 작동합니다.")

except Exception as e:
    print("\n❌ [최종 결과] 연결 실패! 에러 메시지를 확인하세요:")
    print("=" * 60)
    print(e)
    print("=" * 60)
    
    print("\n💡 [원인 진단 팁]")
    if "DNS" in str(e):
        print("👉 여전히 DNS 에러가 난다면, 현재 연결된 인터넷(회사 보안망, 특정 공유기 등)이 몽고DB 주소를 차단한 것입니다.")
        print("   노트북이나 PC 인터넷을 [스마트폰 핫스팟]으로 연결하고 이 코드를 다시 실행해 보세요!")

