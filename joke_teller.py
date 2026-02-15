import streamlit as st
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Joke Teller", page_icon="😂", layout="centered")

st.title("😂 Joke Teller Agent")
st.markdown("Welcome! I'm your AI comedian. Tell me what type of jokes you want to hear!")

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

joke_teller = Agent(
    role="joke teller",
    goal="tell hilarious jokes based on the user's preferred type",
    backstory="you are a professional comedian who loves to make people laugh with your creative and entertaining jokes",
    llm=llm
)

joke_judge = Agent(
    role="joke judge",
    goal="evaluate and rate jokes on a scale of 1-10 with constructive feedback",
    backstory="you are an experienced comedy critic who has judged comedy shows for decades",
    llm=llm
)

joke_type = st.text_input(
    "What type of jokes do you want to hear?",
    placeholder="e.g., dad jokes, puns, knock-knock jokes, programming jokes, dark humor..."
)

if st.button("Tell me a joke!", type="primary"):
    if not joke_type.strip():
        st.warning("Please enter a joke type first!")
    else:
        with st.spinner("🎭 Our comedian is crafting the perfect joke for you..."):
            joke_task = Task(
                description=f"Create a hilarious {joke_type} joke. Make it creative, original, and actually funny!",
                expected_output="A funny joke of the requested type",
                agent=joke_teller
            )

            judge_task = Task(
                description="Review the joke created and provide: 1) The original joke, 2) A rating out of 10, 3) Brief feedback on why it's funny or not",
                expected_output="The joke, a rating (1-10), and short critique",
                agent=joke_judge,
                context=[joke_task]
            )

            crew = Crew(
                agents=[joke_teller, joke_judge],
                tasks=[joke_task, judge_task],
                verbose=False
            )

            result = crew.kickoff()

        st.success("Here's your joke!")
        st.markdown("---")
        st.markdown(f"**🎤 Joke Type:** {joke_type}")
        st.markdown(f"**😄 Result:**")
        st.write(result.raw)

st.markdown("---")
st.caption("Powered by CrewAI + Streamlit | Made with ❤️ to make you laugh")