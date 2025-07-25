import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os

st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도 만들기")

SAVE_FILE = "bookmarks.csv"

# 초기 북마크 로드
if "bookmarks" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        st.session_state.bookmarks = pd.read_csv(SAVE_FILE).to_dict("records")
    else:
        st.session_state.bookmarks = []

# 클릭된 좌표 기억
if "clicked_location" not in st.session_state:
    st.session_state.clicked_location = None

# 중심 위치
if st.session_state.bookmarks:
    center = [st.session_state.bookmarks[-1]["위도"], st.session_state.bookmarks[-1]["경도"]]
else:
    center = [37.5665, 126.9780]

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

# 지도 출력 + 클릭 좌표 얻기
map_data = st_folium(m, width=1000, height=600, returned_objects=["last_clicked"])

# 클릭 좌표 표시
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.session_state.clicked_location = (lat, lon)
    st.info(f"🖱️ 클릭한 위치의 위도: `{lat:.6f}`, 경도: `{lon:.6f}`")

# 👉 북마크 추가 폼
with st.sidebar.form("bookmark_form"):
    st.subheader("📌 북마크 추가")
    name = st.text_input("장소 이름")
    lat_default, lon_default = (st.session_state.clicked_location if st.session_state.clicked_location else (0.0, 0.0))
    lat = st.number_input("위도", value=lat_default, format="%.6f")
    lon = st.number_input("경도", value=lon_default, format="%.6f")
    desc = st.text_area("설명", height=80)
    submitted = st.form_submit_button("추가하기")  # ✅ 이 줄이 필수

    if submitted and name:
        new_entry = {"이름": name, "위도": lat, "경도": lon, "설명": desc}
        st.session_state.bookmarks.append(new_entry)
        pd.DataFrame(st.session_state.bookmarks).to_csv(SAVE_FILE, index=False)
        st.success(f"✅ '{name}' 북마크가 저장되었습니다!")

# 👉 북마크 삭제 폼
with st.sidebar.form("delete_form"):
    st.subheader("🗑️ 북마크 삭제")
    bookmark_names = [bm["이름"] for bm in st.session_state.bookmarks]
    if bookmark_names:
        selected_to_delete = st.selectbox("삭제할 북마크 선택", bookmark_names)
        delete = st.form_submit_button("삭제하기")  # ✅ 이 줄이 필수
        if delete:
            st.session_state.bookmarks = [bm for bm in st.session_state.bookmarks if bm["이름"] != selected_to_delete]
            pd.DataFrame(st.session_state.bookmarks).to_csv(SAVE_FILE, index=False)
            st.success(f"❌ '{selected_to_delete}' 북마크가 삭제되었습니다.")
    else:
        st.write("저장된 북마크가 없습니다.")

# 북마크 목록 표시
with st.expander("📋 북마크 목록 보기"):
    if st.session_state.bookmarks:
        st.dataframe(pd.DataFrame(st.session_state.bookmarks))
    else:
        st.write("저장된 북마크가 없습니다.")
