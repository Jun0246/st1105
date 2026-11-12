import streamlit as st

classcode="1234"
code = st.text_input("클래스 코드를 입력하세요")

# 코드가 1234이면 화면에 "환영합니다". 아니면 "돌아가세요" 출력
if code == "":
    st.write("코드를 입력하세요")
elif code == classcode:
    st.success("환영합니다")
else:
    st.error("돌아가세요")



st.subheader("다양한 인풋")

#객관식(라디오버튼, 체크박스), 주관식(숫자, 텍스트, LateX), 슬라이더, 파일업로드

#답은 -2

answer = st.radio("x+2=0의 해는?",("-2","-1","0","1","2"))
if answer == "-2":
    st.success("정답입니다")
elif answer == "2":
    st.error("부호를 잘 생각해봅시다.")
else:
    st.warning("다시 생각해봅시다.")


agree = st.checkbox("I agree")

if agree == True:
    st.success("동의하셨습니다")
else:
    st.error("동의하지 않았습니다") 

answer2 = st.text_input("답을 입력하세요", placeholder="x^2-1=0의 해는?")

if answer2  == "":
    st.write("답을 입력하세요")
else:
    st.success("정답입니다")

answer3 = st.number_input("숫자를 입력하세요", 
min_value=0, max_value=100, step=10, 
value=50,)

if st.button("제출"):
    if answer3 == 50:
        st.success("정답입니다")
    else:
        st.error("틀렸습니다")

# 라디오버튼 문제에 대한 답에 따른 피드백 제공
answer4 = st.radio(
    "기울기가 가장 큰 것은?",
    ("y=x", "y=2x", "y=-x", "y=-2x"),
    key="radio_answer",
)
if st.button("정답"):
    if answer4 == "y=2x":
        st.success("정답입니다")
    elif answer4 == "y=-2x":
        st.error("부호를 잘 생각해봅시다.")
    else:
        st.warning("다시 생각해봅시다.")
