import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh

# =================================================================
# 🚨 [중요 설정] 5초마다 자동으로 화면을 새로고침하여 양방향 동기화 유지
# 컴퓨터든 핸드폰이든 가만히 있어도 5초마다 DB 최신 상태를 읽어옵니다.
# =================================================================
st_autorefresh(interval=5000, limit=9999, key="db_sync_counter")

st.set_page_config(page_title="다이아몬드 툴 관리 시스템", layout="wide")

st.title("🏭 4PART (검색/필터 기능)")
st.write("사무실 및 현장관리용 (실시간 클라우드 DB 양방향 연동)")
st.markdown("---")

# =================================================================
# 🔌 [MongoDB Atlas 연결 설정]
# 반드시 회원님의 실제 MongoDB 연결 주소(ID, PW 포함)를 입력하세요.
# 예: "mongodb+srv://사용자ID:비밀번호@cluster0...mongodb.net/..."
# =================================================================
MONGO_URI = "mongodb+srv://sspon1270_db_user:wXA7NGCMjjTiTG5w@cluster0.lectnsv.mongodb.net/?retryWrites=true&w=majority"

# 캐시 없이 매번 함수가 실행될 때마다 실시간으로 DB에 직접 꽂히도록 연결 설정
def get_mongo_collection():
    client = MongoClient(MONGO_URI)
    db = client["tool_manager"]  # 데이터베이스 이름
    return db["tools"]           # 컬렉션(테이블) 이름

try:
    collection = get_mongo_collection()
except Exception as e:
    st.error(f"❌ 데이터베이스 연결 실패: {e}")

# --- DB에서 최신 데이터를 실시간으로 가져오는 함수 ---
def load_live_data():
    try:
        # 캐시를 쓰지 않고 무조건 실시간으로 MongoDB에서 전체 데이터를 긁어옴
        live_data = list(collection.find({}, {"_id": 0}))
        
        # 만약 DB가 완전히 비어있다면, 시스템이 정상 작동하도록 샘플 초기 데이터를 DB에 강제 주입
        if not live_data:
            sample_data = [
                {"툴ID": "4P260529-200161", "툴종류": "#200전착", "상태": "사용중", "입고날짜": "2026-05-29", "장착기계": "#3호기", "가공제품": "하우징A", "가공수량": 150},
                {"툴ID": "4P260529-200162", "툴종류": "#200전착", "상태": "재연마 필요", "입고날짜": "2026-05-29", "장착기계": "#2호기", "가공제품": "하우징B", "가공수량": 420},
                {"툴ID": "4P260530-200163", "툴종류": "#200전착", "상태": "폐기완료", "입고날짜": "2026-05-30", "장착기계": "#1호기", "가공제품": "커버C", "가공수량": 850},
                {"툴ID": "4P260601-300001", "툴종류": "#400레진", "상태": "신품", "입고날짜": "2026-06-01", "장착기계": "미장착", "가공제품": "없음", "가공수량": 0},
                {"툴ID": "4P260602-200164", "툴종류": "#200전착", "상태": "사용중", "입고날짜": "2026-06-02", "장착기계": "#3호기", "가공제품": "하우징A", "가공수량": 95}
            ]
            collection.insert_many(sample_data)
            live_data = sample_data
            
        return pd.DataFrame(live_data)
    except Exception as e:
        st.error(f"⚠️ 데이터를 불러오는 중 오류 발생: {e}")
        return pd.DataFrame()

# 갱신된 최신 데이터프레임 확보
current_df = load_live_data()

# 화면을 왼쪽(입력창)과 오른쪽(검색 및 테이블)으로 나눕니다.
col1, col2 = st.columns([1, 2])

# --- 왼쪽: 현장 정보 입력 및 수정 칸 ---
with col1:
    st.subheader("📥 툴 정보 등록/수정")
    target_id = st.text_input("🆔 대상 툴 고유번호 입력", value="4P260529-200161")
    
    in_date = st.date_input("📅 입고 날짜", value=pd.Timestamp.now().date())
    mount_date = st.date_input("🛠️ 기계 장착 날짜", value=pd.Timestamp.now().date())
    
    machine_num = st.text_input("🤖 장착 기계 번호", value="#3호기")
    product_name = st.text_input("📦 가공 제품명", value="스마트폰 하우징A")
    tool_status = st.selectbox("💡 현재 툴 상태", ["신품", "사용중", "재연마 필요", "폐기완료"])
    qty = st.number_input("🔢 가공 수량 (개)", min_value=0, value=150)
    
    if st.button("🚀 설정된 값으로 DB 업데이트"):
        new_row = {
            "툴ID": target_id, 
            "툴종류": "#200전착" if "20" in target_id else "#400레진", 
            "상태": tool_status, 
            "입고날짜": str(in_date), 
            "장착기계": machine_num, 
            "가공제품": product_name, 
            "가공수량": qty
        }
        
        try:
            # 💡 [핵심] 툴ID가 일치하는 녀석이 있으면 덮어쓰고(Update), 없으면 새로 추가(Insert) 합니다.
            collection.update_one(
                {"툴ID": target_id},
                {"$set": new_row},
                upsert=True
            )
            st.success(f"✅ {target_id} 툴 정보가 데이터베이스에 실시간 저장되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ 데이터베이스 저장 실패: {e}")

# --- 오른쪽: 대망의 검색 및 데이터 시트 현황 조회 ---
with col2:
    st.subheader("🔍 실시간 데이터베이스 검색 및 필터")
    
    # 1. 상단 검색창 구성 (가로로 배치)
    search_cols = st.columns(3)
    
    with search_cols[0]:
        search_keyword = st.text_input("🔎 만능 텍스트 검색 (ID, 기계 등)", value="")
        
    with search_cols[1]:
        filter_status = st.selectbox("🎯 툴 상태 필터", ["전체 보기", "신품", "사용중", "재연마 필요", "폐기완료"])
        
    with search_cols[2]:
        filter_machine = st.selectbox("🤖 기계별 필터", ["전체 보기", "#1호기", "#2호기", "#3호기", "미장착"])

    # 2. [검색 로직 작동] 항상 실시간으로 읽어온 current_df를 기반으로 가공
    filtered_df = current_df.copy()
    
    if not filtered_df.empty:
        if search_keyword:
            filtered_df = filtered_df[
                filtered_df["툴ID"].str.contains(search_keyword, na=False) | 
                filtered_df["장착기계"].str.contains(search_keyword, na=False) |
                filtered_df["가공제품"].str.contains(search_keyword, na=False)
            ]
            
        if filter_status != "전체 보기":
            filtered_df = filtered_df[filtered_df["상태"] == filter_status]
            
        if filter_machine != "전체 보기":
            filtered_df = filtered_df[filtered_df["장착기계"] == filter_machine]

    # 3. 최종 필터링된 결과 테이블 출력
    st.write(f"📊 검색된 툴 개수: **{len(filtered_df)}**개")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.info("💡 실시간 동기화 활성화 중: 핸드폰이나 PC 어느 쪽에서 수정하든 최대 5초 이내에 양쪽 화면이 모두 자동 동기화됩니다.")

