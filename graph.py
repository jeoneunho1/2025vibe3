import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="서울 인구 피라미드", layout="wide")
st.title("👥 서울특별시 연령별 성별 인구 피라미드 (2025년 6월)")

uploaded_file = st.file_uploader("📁 연령별 인구 CSV 업로드 (cp949 인코딩)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
        seoul_df = df[df["행정구역"].str.startswith("서울특별시")].copy()

        # 남/여 연령 컬럼 추출
        male_cols = [c for c in seoul_df.columns if "2025년06월_남_" in c and "총인구수" not in c and "연령구간인구수" not in c]
        female_cols = [c for c in seoul_df.columns if "2025년06월_여_" in c and "총인구수" not in c and "연령구간인구수" not in c]

        ages = []
        males = []
        females = []

        for m_col, f_col in zip(male_cols, female_cols):
            age_str = m_col.split("_")[-1].replace("세", "")
            age = int(age_str) if age_str.isdigit() else 100  # '100세 이상'

            m_val = seoul_df.iloc[0][m_col]
            f_val = seoul_df.iloc[0][f_col]

            # 문자열이면 쉼표 제거
            if isinstance(m_val, str):
                m_val = m_val.replace(",", "")
            if isinstance(f_val, str):
                f_val = f_val.replace(",", "")

            ages.append(age)
            males.append(-int(m_val))  # 왼쪽으로 표시
            females.append(int(f_val))

        # 정렬
        age_df = pd.DataFrame({"나이": ages, "남성": males, "여성": females}).sort_values("나이")

        # Plotly 인구 피라미드
        fig = go.Figure()
        fig.add_trace(go.Bar(y=age_df["나이"], x=age_df["남성"], name="남성", orientation='h', marker_color="royalblue"))
        fig.add_trace(go.Bar(y=age_df["나이"], x=age_df["여성"], name="여성", orientation='h', marker_color="salmon"))

        fig.update_layout(
            title="서울특별시 연령별 인구 피라미드",
            barmode="relative",
            xaxis_title="인구 수",
            yaxis_title="나이",
            xaxis=dict(tickformat=','),
            template="plotly_white",
            height=800
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("⬆️ 좌측에서 연령별 인구 CSV 파일을 업로드해주세요.")
