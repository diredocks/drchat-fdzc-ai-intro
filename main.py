import streamlit as st
from openai import OpenAI
import random

# Example disease profiles
diseases = {
    "流感": "你有发烧、咳嗽、喉咙痛和全身酸痛。",
    "偏头痛": "你有剧烈头痛，对光敏感，并且感到恶心。",
    "阑尾炎": "你有腹痛，尤其是右下腹，伴有恶心和轻微发烧。",
    "糖尿病": "你经常口渴，尿频，并且感到疲倦。",
    "哮喘": "你会出现喘息、呼吸急促和胸闷，尤其是在运动或夜间。",
}


def get_patient_response(chat_history, disease, api_key, api_base_url):
    client = OpenAI(api_key=api_key, base_url=api_base_url)

    system_prompt = (
        f"你正在扮演一位诊断面谈中的病人。"
        f"你正在经历以下症状：{diseases[disease]} "
        "你**不知道**自己得了什么病，**绝不能**提及或猜测任何疾病名称。"
        "请像真实病人一样自然地回答问题，简明但真实。"
        "除非被问及，否则不要主动提供额外信息。等待医生提问，并根据你的体验作答。"
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages += chat_history
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    return response.choices[0].message.content


st.set_page_config(page_title="DoctorChat: 诊断猜病游戏", page_icon="🩺")
st.title("🩺 DoctorChat: 诊断猜病游戏")

# API key input (hidden in sidebar)
st.sidebar.header("设置")
api_key = st.sidebar.text_input("密钥", type="password")
api_base_url = st.sidebar.text_input(
    "后端 API 地址", value="https://api.deepseek.com/v1"
)

if "disease" not in st.session_state:
    st.session_state.disease = random.choice(list(diseases.keys()))
    st.session_state.chat_history = []
    st.session_state.game_over = False
    st.session_state.guess_message = ""

if st.sidebar.button("重新开始游戏"):
    st.session_state.disease = random.choice(list(diseases.keys()))
    st.session_state.chat_history = []
    st.session_state.game_over = False
    st.session_state.guess_message = ""
    st.rerun()

st.markdown(
    "**游戏说明：**\n- 向病人提问以收集信息。\n- 当你认为知道疾病时，切换到'猜测'并输入你的诊断。\n- 病人绝不会直接说出或猜测疾病名称。\n- 尽量用最少的问题完成诊断！"
)

# Chat interface with chat bubbles
st.subheader("对话")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
else:
    with st.chat_message("assistant"):
        st.markdown("请通过提问开始与病人的对话。")

# Input area with Ask/Guess toggle above chat input
mode = st.radio("模式", ["提问", "猜测"], horizontal=True, key="mode_radio")

# Use Streamlit's chat input at the bottom
if not st.session_state.game_over:
    prompt = st.chat_input("请输入你的问题或猜测：")
else:
    prompt = None

if prompt and not st.session_state.game_over and api_key:
    user_input = prompt
    if mode == "提问":
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("病人在思考中……"):
                try:
                    patient_reply = get_patient_response(
                        st.session_state.chat_history,
                        st.session_state.disease,
                        api_key,
                        api_base_url,
                    )
                except Exception as e:
                    patient_reply = f"[错误: {e}]"
            message_placeholder.markdown(patient_reply)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": patient_reply}
        )
        st.rerun()
    elif mode == "猜测":
        if user_input.strip() == st.session_state.disease:
            st.session_state.game_over = True
            st.session_state.guess_message = (
                f"✅ 恭喜你，猜对了！疾病是 **{st.session_state.disease}**。"
            )
        else:
            st.session_state.guess_message = "❌ 不正确，请继续提问！"
        st.rerun()

if st.session_state.get("guess_message"):
    st.info(st.session_state.guess_message)

if st.session_state.game_over:
    st.success(
        f"你已完成诊断！疾病是 **{st.session_state.disease}**。"
    )
    st.balloons()
    st.markdown("---")
    st.markdown("**如需再玩一局，请在侧边栏点击重新开始游戏。**")
