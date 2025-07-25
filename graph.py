import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="서울 연령별 인구 시각화", layout="wide")
st.title("👶 서울특별시 연령별 인구 분포 (2025년 6월 기준)")

# 파일 업로드
uploaded_file = st.file_uploader("📁 연령별 인구 CSV 파일 업로드 (cp949 인코딩)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")

        # 서울특별시만 필터링
        seoul_df = df[df["행정구역"].str.startswith("서울특별시")].copy()

        # 연령 컬럼 필터
        age_columns = [col for col in seoul_df.columns if "2025년06월_계_" in col and "총인구수" not in col and "연령구간인구수" not in col]

        # 나이/인구 리스트 생성
        ages = []
        values = []

        for col in age_columns:
            age_str = col.split("_")[-1].replace("세", "")
            age = int(age_str) if age_str.isdigit() else 100

            raw_value = seoul_df.iloc[0][col]
            if isinstance(raw_value, str):
                raw_value = raw_value.replace(",", "")
            count = int(raw_value)

            ages.append(age)
            values.append(count)

        # 정렬
        age_df = pd.DataFrame({"나이": ages, "인구수": values}).sort_values("나이")

        # Plotly 그래프
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=age_df["나이"],
            y=age_df["인구수"],
            marker_color="royalblue"
        ))
        fig.update_layout(
            title="서울특별시 연령별 인구 분포",
            xaxis_title="나이",
            yaxis_title="인구 수",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("⬆️ 왼쪽에서 연령별 인구 CSV 파일을 업로드해주세요.")
