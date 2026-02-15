from crewai import Agent , Task , Crew , LLM
from crewai_tools import ScraperDevTool
from dotenv import load_dotenv 
import os

chatbot = input("enter the topic you want to study about:")

load_dotenv()
search_tool = ScraperDevTool()
ScraperDevTool


llm = LLM(
    model = "gemini/gemini-2.5-flash",
    api_key = os.getenv("GEMINI_API_KEY")
)

resercher_agent = Agent(
    role = "researcher agent",
    goal = "research information with the users input ",
    backstory = "you are a great resercher who studies about the world and space but people didnt take any interest in it",
    llm = llm,
    tools = [search_tool]
)

indentation_agent = Agent(
    role = "indentation agent",
    goal = "indent the answer given by the resercher agent to make it more readable",
    backstory = "you are a english expert teacher who helps people to write the paragraph or whatever in readable format",
    llm = llm,
    tools = [search_tool]
)


reserchers_task = Task(
    description = "research about the topic given by researcher and provide the real information ",
    expected_output = "a useful information about the topic so that if people read this information so they started taking interest in it",
    agent=resercher_agent
)

indentation_agents_task = Task(
    description = "indent the information given by the resercher agent to make it more readable",
    expected_output = "i am sure that the output will be more readable and more understanding",
    agent=indentation_agent
)
crew = Crew(
    agents = [resercher_agent,indentation_agent],
    tasks = [reserchers_task,indentation_agents_task],
    verbose = True 
)

results = crew.kickoff(inputs ={"topic":chatbot})
print(results)
