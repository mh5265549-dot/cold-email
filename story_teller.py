from crewai import Agent , Task , Crew , LLM
from dotenv import load_dotenv
import os

load_dotenv()

llm = LLM(
    model = "groq/llama-3.1-8b-instant",
    api_key = os.getenv("GROQ_API_KEY")
)

story_Teller = Agent(
    role = "story teller",
    goal = "tell a horror story to make the people cry in fear",
    backstory = "you are a horror story writer who loves to scare people with your stories",
    llm = llm
)

story_judge = Agent(
    role = "story judge",
    goal = "judge the story and rate its scariness out of 10",
    backstory = "you are a horror story critic who rates stories for a living",
    llm = llm
)

story_creation = Task(
    description = "create a horror story",
    expected_output = "a scary horror story",
    agent = story_Teller
)

story_judging = Task(
    description = "judge the story created by the story teller",
    expected_output = " rate the story out of 10",
    agent = story_judge
)

crew = Crew(
    agents = [story_Teller , story_judge],
    tasks = [story_creation , story_judging],
    verbose = True
)

results = crew.kickoff()
print(results)
