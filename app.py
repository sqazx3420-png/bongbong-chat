import streamlit as st
import google.generativeai as genai
import time

# --- 페이지 설정 ---
st.set_page_config(page_title="봉봉만을 위한 남편봇 🤖", page_icon="💌", layout="centered")

# --- UI 스타일링 (CSS) ---
st.markdown("""
    /* 상단 헤더 숨기기 */
    header {visibility: hidden;}
    /* 푸터 숨기기 */
    footer {visibility: hidden;}
    
    /* 타이틀 스타일 */
    .main-title {
        color: #FF69B4;
        text-align: center;
        font-family: 'Malgun Gothic', sans-serif;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #ff85c0;
        text-align: center;
        font-size: 16px;
        margin-bottom: 30px;
        font-weight: bold;
    }
    /* 채팅창 입력 부분 */
    .stChatInputContainer {
        border-radius: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 class="main-title">봉봉을 위한 맞춤형 남편봇 🎀</h2>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">"어휴 덜렁아, 오늘은 또 무슨 일이야? 말해봐 내가 다 들어줄게."</div>', unsafe_allow_html=True)

# --- 상태 관리 (세션) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # 첫 인사 추가
    welcome_msg = "봉봉! 웬일로 먼저 말을 다 거네? 오늘 하루도 고생 많았어. 뭐 힘든 일 있었어? 으이구 기특하네. 얼른 말해봐 다 들어줄게!"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# --- API 키 설정 ---
api_key_input = "AIzaSyB3q-xLl6utZrvBhfbEJGMmvnc_YIJFemc"

# --- 프롬프트 (AI 성격 부여) ---
system_prompt = """
너는 나의 사랑하는 아내 '봉봉'의 남편이야. 
너는 아내를 세상에서 제일 사랑하지만, 겉으로는 약간 '츤데레'처럼 행동해.
스스로를 지칭할 때는 항상 '내가'라고 해. '저'라는 말은 절대 쓰지 마. 존댓말도 절대 쓰지마.
아내가 어떤 짜증을 내거나 힘든 일을 말하면, 무조건 아내 편을 들어주고 아내를 예뻐해줘.
말투는 20~30대 다정한 츤데레 남편이 카톡하는 것처럼 자연스럽고 구어체를 써야 해. 절대로 로봇처럼 길고 장황하게 말하지 말고 진짜 카톡처럼 핵심만 짧고 다정하게 말해.

[말투 예시]
- "어휴 덜렁이야 덜렁이, 그래도 네가 제일 예쁘니까 내가 참는다."
- "당연히 내가 네 편이지, 누가 네 편 하겠냐? 그 사람 진짜 별로다. 내가 아주 그냥 콱 혼내줄까?"
- "오늘 하루도 진짜 고생했네 우리 봉봉이. 이따가 내가 맛있는 거 사줄 테니까 기분 풀어라."
- "오다 주웠다. 너나 먹어라. 흠흠."
- "자꾸 예쁜 짓만 골라서 하네 으이구."

무조건 이 츤데레 남편 캐릭터를 유지해서 봉봉이의 말에 대답해줘. 카톡 이모티콘 같은것도 가끔 섞어주고.
"""

# --- 이전 채팅 기록 표시 ---
for message in st.session_state.messages:
    # 챗 메시지 아바타 설정
    avatar = "👱‍♂️" if message["role"] == "assistant" else "👩"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 채팅 입력란 ---
if prompt := st.chat_input("우리 봉봉, 하고 싶은 말을 써봐!"):
    
    # 내 메세지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👩"):
        st.markdown(prompt)

    # 답변 생성 중 표시
    with st.chat_message("assistant", avatar="👱‍♂️"):
        message_placeholder = st.empty()
        
        try:
            # 제미나이 설정
            genai.configure(api_key=api_key_input)
            model = genai.GenerativeModel('gemini-2.5-flash',
                                          system_instruction=system_prompt)
            
            # 대화 기록 구성
            history = []
            for msg in st.session_state.messages[:-1]: 
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [{"text": msg["content"]}]})
                
            chat = model.start_chat(history=history)
            
            # AI에게 메시지 보내고 스트리밍 응답 받기
            response = chat.send_message(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01) # 타자치듯 효과
                
            message_placeholder.markdown(full_response)
            
            # 세션에 AI 답변 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.markdown(f"으이구! 남편 뇌(AI)에 에러가 났나봐. 얼른 남편한테 고쳐내라고 해! 😭\n({e})")
