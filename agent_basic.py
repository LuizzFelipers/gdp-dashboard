from agno.agent import Agent
from agno.tools.tavily import TavilyTools
from agno.models.groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[TavilyTools()],
    debug_mode= True
)

agent.print_response("Use suas ferramentas de pesquisa para informar qual será a temperatura de amanhã em Brasília")
