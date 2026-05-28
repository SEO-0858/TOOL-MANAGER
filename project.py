import streamlit as st
import qrcode
import pandas as pd
from pymongo import MongoClient
import certifi
import io

# --- 1. 회사 방화벽을 우회하는 일반 표준 URL 설정 ---
MONGO_URI = (
    "mongodb://sspon1270_db_user:wXA7NGCMjjTiTG5w@"
    "ac-lectnsv-shard-00-00.lectnsv.mongodb.net:27017,"
    "ac-lectnsv-shard-00-01.lectnsv.mongodb.net:27017,"
    "ac-lectnsv-shard-00-02.lectnsv.mongodb.net:27017/"
    "?ssl=true&authSource=admin&replicaSet=atlas-lectnsv-shard-0&retryWrites=true&w=majority"
)

@st.cache_resource
def get_mongo_client():
    # 클라우드 서버 환경에서도 안전하게 SSL 인증을 통과하도록 설정
    return MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# 데이터베이스 연결 상태 확인
try:
    client = get_mongo_client()
    db = client["SmartFactory"]          
    collection = db["MeasurementData"]   
    client.admin.command('ping') # 연결 확인용 핑
    connection_success = True
except Exception as e:
    connection_success = False
    connection_error_msg = str(e)


# --- 2. 화면 우측 사이드바에 현재 페이지 QR코드 자동 표시 ---
# 클라우드에 배포되면 자동으로 주소를 인식하여 QR코드를 동적으로 생성합니다.
try:
    # 현재 웹페이지의 실제 URL 주소를 가져옴
    from streamlit.web.server.server import Server
    current_url = st.to_container_width
    # 만약 주소를 가져오기 힘들 경우를 대비한 안전장치
    if not current_url:
        current_url = "https://share.streamlit.io/"
except:
    current_url = "https://share.streamlit.io/"

def generate_qr_bytes(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# 사이드바에 QR코드 그리기 (인쇄하거나 다른 핸드폰으로 찍을 때 사용)
st.sidebar.header("📱 스마트폰 접속 QR")
st.sidebar.write("이 대시보드를 스마트폰으로 보시려면 아래 QR코드를 스캔하세요.")
qr_bytes = generate_qr_bytes(current_url)
st.sidebar.image(qr_bytes, caption="스마트폰 스캔용 QR", use_container_width=True)


# --- 3. 메인 웹 대시보드 화면 구성 ---
st.title("🏭 클라우드 생산 데이터 대시보드")

if connection_success:
    st.success("🟢 클라우드 데이터베이스(MongoDB)와 성공적으로 연결되었습니다.")
else:
    st.error("🔴 데이터베이스 연결에 실패했습니다. 코드가 클라우드 서버에 배포되면 정상 연결될 수 있습니다.")
    st.code(connection_error_msg, language="bash")

st.markdown("---")

# [기능 1] 스마트폰/컴퓨터에서 데이터 입력 및 MongoDB 저장
st.header("📝 새 측정 데이터 등록")
st.write("스마트폰으로 이 페이지에 접속하여 데이터를 입력하고 저장해 보세요.")

with st.form(key="factory_input_form", clear_on_submit=True):
    worker = st.text_input("작업자 성명", value="서동일")
    part_name = st.text_input("부품명/공정명", value="#170METAL")
    measured_val = st.number_input("측정 수치 (mm)", value=100pie, format="%.3f")
    status = st.selectbox("판정 결과", ["합격(PASS)", "재검사(REWORK)", "불량(FAIL)"])
    
    submit = st.form_submit_button(label="🚀 클라우드 DB에 데이터 저장")

if submit and connection_success:
    
    data_payload = {
        "작업자": worker,
        "부품명": part_name,
        "측정값": measured_val,
        "판정": status,
        "시간": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    try:
        collection.insert_one(data_payload)
        st.success("🎉 데이터가 외부 MongoDB 클라우드에 안전하게 기록되었습니다!")
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {e}")

st.markdown("---")

# [기능 2] MongoDB에 쌓인 데이터를 실시간으로 조회하여 테이블로 표시
st.header("📊 실시간 모니터링 현황")
if connection_success:
    try:
        # DB에서 최신 데이터들을 읽어옴 (_id 고유값은 뺌)
        mongo_data = list(collection.find({}, {"_id": 0}))
        if mongo_data:
            df = pd.DataFrame(mongo_data)
            # 최신 입력 데이터가 표의 맨 위에 보이도록 정렬 변환
            st.dataframe(df.iloc[::-1], use_container_width=True)
        else:
            st.info("현재 저장된 데이터가 없습니다. 첫 데이터를 입력해 보세요!")
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")