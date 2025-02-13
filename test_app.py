import streamlit as st
import pandas as pd
import io

# 📌 페이지 설정
st.set_page_config(page_title="국내선물 마디 계산기", page_icon="📈")

# 📌 제목 및 설명
st.title("📈 국내선물 마디 계산기")
st.markdown("📌 **시가를 입력하면 위로 24마디, 아래로 24마디를 자동 계산합니다.**")

# 📌 시가 입력
price = st.number_input("💰 시가 입력", min_value=0.0, format="%.2f")

# 📊 마디 간격 리스트
c_values = [
    0.6, 0.55, 0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55,
    0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55, 0.7, 0.65,
    0.6, 0.75, 0.5, 0.65,
    0,  # 시가
    0.6, 0.55, 0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55,
    0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55, 0.7, 0.65,
    0.6, 0.75, 0.5, 0.65
]

if price:
    # 📌 가격 계산
    upper_prices = [price]
    for gap in reversed(c_values[:24]):  
        upper_prices.insert(0, round(upper_prices[0] + gap, 2))

    lower_prices = [price]
    for gap in c_values[25:]:  
        lower_prices.append(round(lower_prices[-1] - gap, 2))

    final_prices = upper_prices[:-1] + [price] + lower_prices[1:]
    madi_numbers = list(range(24, 0, -1)) + ["시가"] + list(range(1, 25))

    # ✅ 오류 검증 (assert 대신 사용자 친화적 오류 메시지)
    if len(final_prices) != 49:
        st.error(f"🚨 가격 리스트 길이 오류 발생: {len(final_prices)} (49 필요)")
        st.stop()

    # 📌 데이터프레임 생성
    df = pd.DataFrame({
        "마디 번호": madi_numbers,
        "계산된 가격": [f"{p:.2f}" for p in final_prices],
        "마디 간격": [str(int(gap)) if gap.is_integer() else f"{gap:.2f}" for gap in c_values]
    })

    # 📌 색상 스타일 적용
    def highlight_rows(row):
        try:
            idx = df.index.get_loc(row.name)
            if row["마디 번호"] == "시가":
                return ["background-color: lightgreen"] * len(row)
            elif idx < 24:
                return ["background-color: lightsalmon"] * len(row)
            else:
                return ["background-color: lightblue"] * len(row)
        except KeyError:
            return [""] * len(row)

    styled_df = df.style.apply(highlight_rows, axis=1)

    # 📊 표 출력 (st.dataframe() 대신 st.table() 사용)
    st.table(styled_df)

    # 📥 엑셀 다운로드 기능
    @st.cache_data
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="마디 계산")
        return output.getvalue()

    xlsx_data = convert_df_to_excel(df)

    st.download_button(
        label="📥 엑셀 다운로드",
        data=xlsx_data,
        file_name="마디_계산.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
