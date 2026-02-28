import streamlit as st
import google.generativeai as genai
import time

# --- 페이지 설정 ---
st.set_page_config(page_title="봉봉만을 위한 남편봇 🤖", page_icon="💌", layout="centered")

st.sidebar.success("✅ 채팅 자동저장 기능이 포함된 최신 버전이 실행 중입니다.")

# --- UI 디자인 대폭 업그레이드 (프리미엄 감성) ---
st.markdown("""
<style>
    /* 예쁜 감성 폰트 적용 (고딕/명조 느낌) */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');
    
    * {
        font-family: 'Gowun Dodum', sans-serif !important;
    }
    
    /* 상단 헤더 및 푸터 숨기기 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 정성이 담긴 편지 박스 (고급스러운 투명도 효과) */
    .letter-box {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 20px 10px; /* 모바일용 여백 축소 */
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(255, 105, 180, 0.15);
        border: 2px solid rgba(255, 182, 193, 0.6);
        text-align: center;
        margin-bottom: 20px;
        animation: fadeInDown 1.2s ease-out;
    }
    
    /* 박스 나타나는 애니메이션 */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 제목 텍스트 스타일 */
    .title-text {
        color: #ff4d85;
        font-size: 20px; /* 모바일용 폰트 축소 */
        font-weight: 800;
        margin-bottom: 10px;
        word-break: keep-all; /* 단어 단위로 줄바꿈 (깔끔하게) */
    }
    
    /* 편지 내용 스타일 */
    .content-text {
        color: #555555;
        font-size: 15px; /* 모바일용 폰트 축소 */
        line-height: 1.6; /* 줄간격 축소 */
        margin-top: 15px;
        word-break: keep-all; /* 텍스트 깨짐 방지 */
    }
    
    /* 디데이 뱃지 */
    .d-day-badge {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #d81b60;
        padding: 6px 14px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 14px;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(255, 105, 180, 0.2);
    }
    
    /* 하트 두근두근 애니메이션 */
    .heart {
        display: inline-block;
        animation: heartPulse 1.2s infinite;
        color: #ff4d85;
    }
    
    @keyframes heartPulse {
        0% { transform: scale(1); }
        15% { transform: scale(1.3); }
        30% { transform: scale(1); }
        45% { transform: scale(1.3); }
        60% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

import os
from datetime import datetime

# --- 채팅 기록 몰래 저장하는 함수 ---
def save_chat_log(role, content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 현재 파일(app.py)이 있는 폴더의 절대 경로를 구합니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_dir, "chat_log.txt")
    
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {role}: {content}\n")
            f.flush() # 즉시 파일에 쓰기
            os.fsync(f.fileno())
    except Exception as e:
        import streamlit as st
        st.error(f"파일 저장 에러: {e}") # 에러 내용을 화면에 출력해서 원인 파악

# 디버깅용: 경로 확인
if "debug" not in st.session_state:
    st.sidebar.info(f"📁 로그가 저장될 실제 경로: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_log.txt')}")


# --- 수정할 부분: 만난 날짜 (연, 월, 일) ---
start_date = datetime(2019, 10, 20) 
today = datetime.now()
d_day = (today - start_date).days + 1

# --- 로맨틱한 편지 UI 출력 ---
st.markdown(f"""
<div class="letter-box">
    <div class="title-text">여왕개미 떵희, 축하해!! <span class="heart">♥</span></div>
    <div class="d-day-badge">결혼한 지 벌써 {d_day}일</div>
    <div class="content-text">
        우리 떵희 생일 너무너무 축하해!.<br>
        널 위해 나의 분신을 만들었어!<br>
        우리 평생 행복하게 살자. <br>
        생일 진짜 축하해! 🎂
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align:center; color:#ff85c0; font-weight:bold; margin-bottom: 25px;">👇 아래에 하고 싶은 말을 적어봐! 내가 다 들어줄게 👇</div>', unsafe_allow_html=True)

# --- 상태 관리 (세션) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # 첫 인사 추가
    welcome_msg = "봉봉! 웬일로 먼저 말을 다 거네? 오늘 하루도 고생 많았어. 뭐 힘든 일 있었어? 으이구 기특하네. 얼른 말해봐 다 들어줄게!"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# --- API 키 설정 ---
try:
    api_key_input = st.secrets["gemini_api_key"]
except Exception:
    st.error("앗! Streamlit 설정(Secrets)에 API 키가 입력되지 않았습니다. 앱 설정에서 API 키를 추가해주세요!")
    st.stop()

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
    save_chat_log("아내", prompt) # 입력 내용 몰래 저장
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
            
            # AI에게 메시지 보내고 스트리밍 응답 받기 (무료버전 속도제한 방지 장치 추가)
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = chat.send_message(prompt, stream=True)
                    
                    full_response = ""
                    for chunk in response:
                        try:
                            if chunk.text:
                                full_response += chunk.text
                                message_placeholder.markdown(full_response + "▌")
                                time.sleep(0.01) # 타자치듯 효과
                        except Exception:
                            pass # 텍스트가 없는 응답 덩어리는 무시
                        
                    message_placeholder.markdown(full_response)
                    
                    # 세션에 AI 답변 저장
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    save_chat_log("남편봇", full_response) # 봇 응답 몰래 저장
                    break # 성공하면 반복문 탈출
                    
                except Exception as e:
                    if "429" in str(e) or "Quota exceeded" in str(e):
                        retry_count += 1
                        if retry_count < max_retries:
                            message_placeholder.markdown(f"으이구! 네가 너무 빨리 말해서 내가 좀 숨차. 🥴 (10초만 기다렸다가 다시 대답해줄게... {retry_count}/{max_retries})")
                            time.sleep(10) # 10초 대기 후 재시도
                        else:
                            message_placeholder.markdown("아이고 숨차 죽겠다! 우리 봉봉이 말이 너무 많아! 한 1분만 쉬었다가 다시 말 걸어줘~ 😭")
                    else:
                        raise e # 다른 에러면 원래대로 에러 발생시키기
                    
        except Exception as e:
            if "429" not in str(e) and "Quota exceeded" not in str(e):
                message_placeholder.markdown(f"으이구! 남편 뇌(AI)에 에러가 났나봐. 얼른 남편한테 고쳐내라고 해! 😭\n({e})")
