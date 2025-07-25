import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석 (1998~2023)")

uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="데이터", engine="openpyxl")

    # 시군구 리스트 필터링
    region_options = df["시군구별"].dropna().unique()
    selected_region = st.selectbox("📍 시도 선택", options=region_options, index=0)

    # 성별 필터
    filtered = df[(df["시군구별"] == selected_region) & (df["성별"].isin(["남자", "여자", "계"]))]

    # 연도 컬럼만 추출
    year_cols = [col for col in filtered.columns if str(col).isdigit()]
    trend = filtered[year_cols]
    trend.index = filtered["성별"].values
    trend = trend.transpose()  # 연도 기준

    # Plotly 꺾은선 그래프
    st.subheader(f"📈 {selected_region}의 남/여/계 자살률 추이")

    fig = go.Figure()
    for gender in trend.columns:
        fig.add_trace(go.Scatter(x=trend.index, y=trend[gender],
                                 mode="lines+markers", name=gender))

    fig.update_layout(title=f"{selected_region} 성별 자살률 추이 (1998~2023)",
                      xaxis_title="연도", yaxis_title="자살률 (명/10만명)",
                      legend_title="성별")

    st.plotly_chart(fig)

else:
    st.info("자살률 통계 엑셀 파일을 업로드해주세요.")
