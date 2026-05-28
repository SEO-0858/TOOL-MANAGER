import streamlit as st
import qrcode
import pandas as pd
from pymongo import MongoClient
import certifi
import io

# --- 1. 가장 안정적인 MongoDB Atlas 공식 표준 주소로 재설정 ---
# Streamlit 클라우드 서버는 회사 방화벽을 안 받으므로 기본 srv 주소가 훨씬 안정적입니다.
MONGO_URI = "mongodb+srv://sspon1270_db_user:wXA7NGCMjjTiTG5w@cluster0.1ectnsv.mongodb.net/SmartFactory?retryWrites=true&w=majority&appName=Cluster0"

@st.cache_resource
def get_mongo_client():
    # tlsCAFile=certifi.where()로 서버 보안 인증을 확실하게 통과시킵니다.
    return MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# 데이터베이스 연결 상태 확인
try:
    client = get_mongo_client()
    db = client["SmartFactory"]          
    collection = db["MeasurementData"]   
    # 서버 연결 테스트 (신호 보내기)
    client.admin.command('ping')
    connection_success = True
except Exception as e:
    connection_success = False
    connection_error_msg = str(e)


# --- 2. 화면 우측 사이드바에 스마트폰 접속용 QR코드 표시 ---
try:
    from streamlit.web.server.server import Server
    current_url = st.to_container_width
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

st.sidebar.header("📱 스마트폰 접속 QR")
st.sidebar.write("이 대시보드를 스마트폰으로 보시려면 아래 QR코드를 스캔하세요.")
qr_bytes = generate_qr_bytes(current_url)
st.sidebar.image(qr_bytes, caption="스마트폰 스캔용 QR", use_container_width=True)


# --- 3. 메인 웹 대시보드 화면 구성 ---
st.title("🏭 클라우드 생산 데이터 대시보드")

if connection_success:
    st.success("🟢 클라우드 데이터베이스(MongoDB)와 성공적으로 연결되었습니다!")
else:
    st.error("🔴 데이터베이스 연결에 실패했습니다. (주소 또는 인증 오류)")
    st.code(connection_error_msg, language="bash")

st.markdown("---")

# [기능 1] 데이터 입력 양식
st.header("📝 새 측정 데이터 등록")
with st.form(key="factory_input_form", clear_on_submit=True):
    worker = st.text_input("작업자 성명", value="서동일")
    part_name = st.text_input("부품명/공정명", value="#170METAL")
    measured_val = st.number_input("측정 수치 (mm)", value=0.0, format="%.3f")
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
        st.sidebar.success("🎉 데이터 저장 성공!")
        st.rerun() # 저장 후 화면 자동 갱신
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {e}")

st.markdown("---")

# [기능 2] 실시간 데이터 조회
st.header("📊 실시간 모니터링 현황")
if connection_success:
    try:
        mongo_data = list(collection.find({}, {"_id": 0}))
        if mongo_data:
            df = pd.DataFrame(mongo_data)
            st.dataframe(df.iloc[::-1], use_container_width=True)
        else:
            st.info("현재 저장된 데이터가 없습니다. 첫 데이터를 입력해 보세요!")
    except Exception as e:
        st.error(f"데이터 로딩 실패: {e}")
