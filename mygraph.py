import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="청소년 여행 경비 분석기", layout="wide")

st.title("🌍 청소년 혼자 여행 경비 + 경로 분석 앱")

uploaded_file = st.file_uploader("📁 여행 일정 및 지출 CSV 파일 업로드", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # 지출 총합 계산
        df["총지출"] = df[["숙박", "식사", "교통", "관광비", "예비비"]].sum(axis=1)

        # 📊 지출 카테고리별 막대 그래프
        st.subheader("📊 카테고리별 총 지출")
        total_by_cat = df[["숙박", "식사", "교통", "관광비", "예비비"]].sum().reset_index()
        total_by_cat.columns = ["항목", "총지출"]

        fig1 = px.bar(total_by_cat, x="항목", y="총지출", color="항목", text="총지출", title="카테고리별 지출")
        st.plotly_chart(fig1, use_container_width=True)

        # 📆 날짜별 총 지출 꺾은선 그래프
        st.subheader("📈 날짜별 총 지출 추이")
        fig2 = px.line(df, x="날짜", y="총지출", markers=True, title="날짜별 지출 추이")
        st.plotly_chart(fig2, use_container_width=True)

        # 🗺️ 여행 경로 지도 시각화
        st.subheader("🗺️ 여행 도시 경로 지도")

        m = folium.Map(location=[36.5, 127.8], zoom_start=6)
        geolocator = Nominatim(user_agent="geoapiExercises")
        coords = []

        for city in df["도시"]:
            try:
                location = geolocator.geocode(city)
                if location:
                    coords.append((location.latitude, location.longitude))
                    folium.Marker([location.latitude, location.longitude], tooltip=city).add_to(m)
            except:
                pass

        # 경로선 그리기
        if len(coords) > 1:
            folium.PolyLine(coords, color="blue", weight=3).add_to(m)

        st_data = st_folium(m, width=700)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("⬆️ CSV 파일을 업로드해주세요. 예: 서울→부산→광주")

