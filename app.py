import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os

st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도 만들기")

# CSV 파일명
SAVE_FILE = "bookmarks.csv"

# 북마크 불러오기
if "bookmarks" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        st.session_state.bookmarks = pd.read_csv(SAVE_FILE).to_dict("records")
    else:
        st.session_state.bookmarks = []

# 북마크 입력 폼
with st.sidebar.form("bookmark_form"):
    st.subheader("📌 북마크 추가")
    name = st.text_input("장소 이름")
    lat = st.number_input("위도", format="%.6f")
    lon = st.number_input("경도", format="%.6f")
    desc = st.text_area("설명", height=80)
    submitted = st.form_submit_button("추가하기")

    if submitted and name:
        new_entry = {
            "이름": name,
            "위도": lat,
            "경도": lon,
            "설명": desc
        }
        st.session_state.bookmarks.append(new_entry)
        pd.DataFrame(st.session_state.bookmarks).to_csv(SAVE_FILE, index=False)
        st.success(f"✅ '{name}' 북마크가 저장되었습니다!")

# 지도 중심 좌표
if st.session_state.bookmarks:
    center = [st.session_state.bookmarks[-1]["위도"], st.session_state.bookmarks[-1]["경도"]]
else:
    center = [37.5665, 126.9780]  # 서울 기본값

# 지도 생성
m = folium.Map(location=center, zoom_start=12)

# 마커 추가
for bm in st.session_state.bookmarks:
    folium.Marker(
        [bm["위도"], bm["경도"]],
        popup=f"<b>{bm['이름']}</b><br>{bm['설명']}" if bm["설명"] else bm["이름"],
        tooltip=bm["이름"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# folium 지도 출력
st_data = st_folium(m, width=1000, height=600)

# 북마크 목록 표시
with st.expander("📋 북마크 목록 보기"):
    st.dataframe(pd.DataFrame(st.session_state.bookmarks))
