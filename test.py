import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os

# 페이지 기본 설정
st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도 만들기")

# 저장 파일
SAVE_FILE = "my_bookmarks.csv"

# 북마크 초기화
if "bookmarks" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        df = pd.read_csv(SAVE_FILE)
        st.session_state.bookmarks = df.to_dict("records")
    else:
        st.session_state.bookmarks = []

# 사이드바 입력
with st.sidebar.form("add_form"):
    st.subheader("📌 북마크 추가하기")
    name = st.text_input("장소 이름")
    lat = st.number_input("위도", format="%.6f")
    lon = st.number_input("경도", format="%.6f")
    desc = st.text_area("설명", height=80)
    add = st.form_submit_button("추가")

    if add and name:
        st.session_state.bookmarks.append({
            "이름": name,
            "위도": lat,
            "경도": lon,
            "설명": desc
        })
        pd.DataFrame(st.session_state.bookmarks).to_csv(SAVE_FILE, index=False)
        st.success(f"'{name}'이(가) 북마크에 추가되었습니다!")

# 중심 위치 계산
if st.session_state.bookmarks:
    last = st.session_state.bookmarks[-1]
    center = [last["위도"], last["경도"]]
else:
    center = [37.5665, 126.9780]  # 서울

# 지도 생성
map = folium.Map(location=center, zoom_start=12)

# 마커 추가
for bm in st.session_state.bookmarks:
    folium.Marker(
        [bm["위도"], bm["경도"]],
        popup=f"<b>{bm['이름']}</b><br>{bm['설명']}" if bm["설명"] else bm["이름"],
        tooltip=bm["이름"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(map)

# 지도 표시
st_data = st_folium(map, width=1000, height=600)

# 북마크 테이블 표시
with st.expander("📋 북마크 목록 보기"):
    st.dataframe(pd.DataFrame(st.session_state.bookmarks))
