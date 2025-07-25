import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os

st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도 만들기")

# 북마크 CSV 파일 경로
BOOKMARKS_FILE = "bookmarks.csv"

# 초기 데이터 불러오기
if "bookmarks" not in st.session_state:
    if os.path.exists(BOOKMARKS_FILE):
        st.session_state.bookmarks = pd.read_csv(BOOKMARKS_FILE).to_dict("records")
    else:
        st.session_state.bookmarks = []

# 입력 폼
with st.sidebar.form("bookmark_form"):
    st.subheader("📌 북마크 추가")
    name = st.text_input("장소 이름")
    lat = st.number_input("위도 (Latitude)", format="%.6f")
    lon = st.number_input("경도 (Longitude)", format="%.6f")
    desc = st.text_area("설명 (선택)", height=80)
    submitted = st.form_submit_button("추가하기")

    if submitted and name:
        st.session_state.bookmarks.append({
            "이름": name,
            "위도": lat,
            "경도": lon,
            "설명": desc
        })
        # 저장
        pd.DataFrame(st.session_state.bookmarks).to_csv(BOOKMARKS_FILE, index=False)
        st.success(f"'{name}' 북마크가 추가되었습니다.")

# 지도 초기 위치 설정
if st.session_state.bookmarks:
    center_lat = st.session_state.bookmarks[-1]["위도"]
    center_lon = st.session_state.bookmarks[-1]["경도"]
else:
    center_lat, center_lon = 37.5665, 126.9780  # 서울 기본값

# folium 지도 생성
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# 마커 추가
for bm in st.session_state.bookmarks:
    popup_html = f"<b>{bm['이름']}</b><br>{bm['설명']}" if bm["설명"] else bm["이름"]
    folium.Marker(
        location=[bm["위도"], bm["경도"]],
        popup=popup_html,
        tooltip=bm["이름"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# 지도 출력
st_data = st_folium(m, width=1000, height=600)

# 북마크 목록 테이블
with st.expander("📋 북마크 목록 보기", expanded=False):
    st.dataframe(pd.DataFrame(st.session_state.bookmarks))
