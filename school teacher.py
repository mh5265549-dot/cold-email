from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import os

load_dotenv()

embedding_work = SentenceTransformerEmbeddingFunction(
    model_name = "all-MINILM-L6-v2"
)

user_topic = input("Enter the topic you want to study (math, science, history): ")

search_tool = SerperDevTool()

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

teacher_agent = Agent(
    role="School Teacher",
    goal="Teach the big students in a seriously way",
    backstory="A rejected school teacher who started a fun tutoring center",
    llm=llm,
    tools=[search_tool]
)

teacher_task = Task(
    description="Teach the topic with simple explanations",
    expected_output="Student understands the topic clearly",
    agent=teacher_agent
)

crew = Crew(
    agents=[teacher_agent],
    tasks=[teacher_task],
    verbose=True
)

result = crew.kickoff(inputs={"topic": user_topic})

print(result)

