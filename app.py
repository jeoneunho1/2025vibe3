import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os
from folium.plugins import MarkerCluster
from io import BytesIO
import base64

st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도 만들기")

SAVE_FILE = "bookmarks.csv"
PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# 🧠 카테고리별 마커 색상
category_colors = {
    "카페": "green",
    "음식점": "red",
    "공부장소": "blue",
    "여행지": "orange",
    "기타": "gray"
}

# 📥 북마크 불러오기 (빈 CSV 및 키 누락 방지)
if "bookmarks" not in st.session_state:
    if os.path.exists(SAVE_FILE):
        try:
            df = pd.read_csv(SAVE_FILE)
            # 누락된 키 초기화
            df["카테고리"] = df.get("카테고리", "기타")
            df["사진"] = df.get("사진", "")
            st.session_state.bookmarks = df.to_dict("records")
        except pd.errors.EmptyDataError:
            st.session_state.bookmarks = []
    else:
        st.session_state.bookmarks = []

# 📌 클릭된 위치 저장
if "clicked_location" not in st.session_state:
    st.session_state.clicked_location = None

# 🔍 검색창
search_term = st.sidebar.text_input("🔍 북마크 검색 (이름/설명 포함)")

# ➕ 북마크 추가
with st.sidebar.form("add_form"):
    st.subheader("➕ 북마크 추가")
    name = st.text_input("장소 이름")
    categories = list(category_colors.keys())
    category = st.selectbox("카테고리", categories)
    lat_default, lon_default = st.session_state.clicked_location if st.session_state.clicked_location else (37.5665, 126.9780)
    lat = st.number_input("위도", value=lat_default, format="%.6f")
    lon = st.number_input("경도", value=lon_default, format="%.6f")
    desc = st.text_area("설명")
    photo = st.file_uploader("사진 업로드 (선택)", type=["jpg", "jpeg", "png"])
    add_button = st.form_submit_button("추가하기")

    if add_button and name:
        photo_path = ""
        if photo:
            photo_path = os.path.join(PHOTO_DIR, f"{name}_{photo.name}")
            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())

        new_entry = {
            "이름": name,
            "카테고리": category,
            "위도": lat,
            "경도": lon,
            "설명": desc,
            "사진": photo_path
        }
        st.session_state.bookmarks.append(new_entry)
        pd.DataFrame(st.session_state.bookmarks).to_csv(SAVE_FILE, index=False)
        st.success(f"✅ '{name}' 북마크가 저장되었습니다!")

# 🗑️ 북마크 삭제
with st.sidebar.form("delete_form"):
    st.subheader("🗑️ 북마크 삭제")
    bookmark_names = [bm["이름"] for bm in st.session_state.bookmarks]
    selected_to_delete = st.selectbox("삭제할 북마크 선택", bookmark_names) if bookmark_names else None
    delete_button = st.form_submit_button("삭제하기")

    if delete_button and selected_to_delete:
        st.session_state.bookmarks = [bm for bm in st.session_state.bookmarks if bm["이름"] != selected_to_delete]
        pd.DataFrame(st.session_state.bookmarks).to_csv(SAVE_FILE, index=False)
        st.success(f"❌ '{selected_to_delete}' 북마크가 삭제되었습니다!")

# 🗺️ 지도 중심
center = st.session_state.clicked_location or \
         ([st.session_state.bookmarks[-1]["위도"], st.session_state.bookmarks[-1]["경도"]] if st.session_state.bookmarks else [37.5665, 126.9780])

# 지도 및 마커 클러스터 생성
m = folium.Map(location=center, zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# 📌 북마크 마커 표시
for bm in st.session_state.bookmarks:
    if search_term and search_term.lower() not in (str(bm.get("이름", "")) + str(bm.get("설명", ""))).lower():
        continue

    popup_html = f"<b>{bm.get('이름', '')}</b><br>{bm.get('설명', '')}<br>📂 카테고리: {bm.get('카테고리', '기타')}"
    photo_path = bm.get("사진", "")
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            popup_html += f'<br><img src="data:image/jpeg;base64,{encoded}" width="150"/>'

    folium.Marker(
        [bm.get("위도", 0), bm.get("경도", 0)],
        popup=popup_html,
        tooltip=bm.get("이름", ""),
        icon=folium.Icon(color=category_colors.get(bm.get("카테고리", "기타"), "gray"), icon="info-sign")
    ).add_to(marker_cluster)

# 🖱️ 클릭 시 위치 저장
map_data = st_folium(m, width=1000, height=600, returned_objects=["last_clicked"])
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.session_state.clicked_location = (lat, lon)
    st.info(f"🖱️ 클릭한 위치 → 위도: `{lat:.6f}`, 경도: `{lon:.6f}`")

# 📋 북마크 목록 보기
with st.expander("📋 북마크 목록 보기"):
    if st.session_state.bookmarks:
        df = pd.DataFrame(st.session_state.bookmarks).drop(columns=["사진"], errors="ignore")
        st.dataframe(df)
    else:
        st.write("📭 등록된 북마크가 없습니다.")
