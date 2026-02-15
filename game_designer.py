from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os

load_dotenv()


user_input = input("Enter the type of game you want to create (e.g., horror, adventure, puzzle): ")

llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)
 
Game_Creator = Agent(
    role="game designer",
    goal="design the game based on the user's prompt",
    backstory="you are a game designer who designed games but was rejected by many companies",
    llm=llm
)

game_reviewer = Agent(
    role="game reviewer",
    goal="review the game and provide constructive feedback",
    backstory="you are a famous game reviewer who reviews games for a living",
    llm=llm
)

game_improver = Agent(
    role="game improver",
    goal="improve the game so it can get a 10 out of 10 rating",
    backstory="you are a game designer who improves games based on reviews",
    llm=llm
)

game_creator = Task(
    description="create the game based on the user's requested game type",
    expected_output="a complete game design document",
    agent=Game_Creator
)

game_review = Task(
    description="review the game created by the game designer",
    expected_output="a review of the game with a rating out of 10",
    agent=game_reviewer
)

game_improvement = Task(
    description="improve the game based on the review",
    expected_output="an improved game design document",
    agent=game_improver
)

crew = Crew(
    agents=[Game_Creator, game_reviewer, game_improver],
    tasks=[game_creator, game_review, game_improvement],
    verbose=True
)

results = crew.kickoff()
print(results)
