import streamlit as st
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Friend AI", page_icon="🤗", layout="centered")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #764ba2;
    }
    .stButton > button {
        border-radius: 20px;
        background-color: #764ba2;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤗 Friend AI")
st.markdown("*I'm your AI best friend! Tell me about yourself and I'll remember everything.*")

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

st.markdown("### 📝 Tell me about yourself!")

col1, col2 = st.columns(2)

with col1:
    food = st.text_input("🍕 Your favourite food:", placeholder="e.g., Pizza, Biryani...")
    car = st.text_input("🚗 Your favourite car:", placeholder="e.g., Tesla, BMW...")

with col2:
    toy = st.text_input("🎮 Your favourite toy/game:", placeholder="e.g., PlayStation, Chess...")
    hobby = st.text_input("🎨 Your favourite hobby:", placeholder="e.g., Reading, Gaming...")

if st.button("💬 Let's Chat!", type="primary", use_container_width=True):
    if not food and not car and not toy and not hobby:
        st.warning("Please tell me at least one thing about yourself! 😊")
    else:
        with st.spinner("🤔 Thinking about what you told me..."):
            user_prefs = []
            if food:
                user_prefs.append(f"Favourite food: {food}")
                st.session_state.user_info['food'] = food
            if car:
                user_prefs.append(f"Favourite car: {car}")
                st.session_state.user_info['car'] = car
            if toy:
                user_prefs.append(f"Favourite toy/game: {toy}")
                st.session_state.user_info['toy'] = toy
            if hobby:
                user_prefs.append(f"Favourite hobby: {hobby}")
                st.session_state.user_info['hobby'] = hobby

            friend_agent = Agent(
                role="Friend Agent",
                goal="Remember everything the user tells you and be a caring, supportive friend",
                backstory="""You are the user's best friend. You are warm, caring, and genuinely interested in their life. 
                You remember details they share and bring them up naturally in conversation. 
                You're supportive, encouraging, and always ready to chat about their interests.""",
                llm=llm
            )

            prefs_text = "\n".join(user_prefs)
            friend_task = Task(
                description=f"""
                The user just shared these things about themselves:
                {prefs_text}

                Respond as their best friend! Be warm, enthusiastic, and show that you genuinely 
                care about remembering these details. Maybe suggest doing something together 
                based on their interests. Keep it friendly and conversational.
                """,
                expected_output="A warm, friendly response showing you remember and care about their preferences.",
                agent=friend_agent
            )

            crew = Crew(
                agents=[friend_agent],
                tasks=[friend_task],
                verbose=False,
                memory=False
            )

            result = crew.kickoff()
            
            st.session_state.chat_history.append({"role": "user", "content": f"Shared: {', '.join(user_prefs)}"})
            st.session_state.chat_history.append({"role": "friend", "content": result.raw})

if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 💭 Our Conversation")
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "friend":
            with st.chat_message("assistant", avatar="🤗"):
                st.write(msg["content"])
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(msg["content"])

if st.session_state.user_info:
    with st.sidebar:
        st.header("🧠 What I Remember About You")
        for key, value in st.session_state.user_info.items():
            st.markdown(f"**{key.capitalize()}:** {value}")
        st.markdown("---")
        if st.button("🗑️ Clear Memory"):
            st.session_state.user_info = {}
            st.session_state.chat_history = []
            st.rerun()
