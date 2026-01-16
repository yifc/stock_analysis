from typing import List
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from tools.calculator_tool import CalculatorTool
from tools.sec_tools import SEC10KTool, SEC10QTool, USER_AGENTS
from tools.yutori_news_tool import YutoriNewsTool
import random

from crewai_tools import ScrapeWebsiteTool

from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (2 directories up from this file)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

from crewai import LLM

# Use Ollama with llama3.1 - runs 100% locally, no rate limits
llm = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")

@CrewBase
class StockAnalysisCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def financial_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'],
            verbose=True,
            llm=llm,
            tools=[
                ScrapeWebsiteTool(headers={'User-Agent': random.choice(USER_AGENTS)}),
                CalculatorTool(),
                SEC10QTool(),
                SEC10KTool(),
            ]
        )
    
    @task
    def financial_analysis(self) -> Task: 
        return Task(
            config=self.tasks_config['financial_analysis'],
            agent=self.financial_agent(),
        )
    

    @agent
    def research_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_analyst'],
            verbose=True,
            llm=llm,
            tools=[
                ScrapeWebsiteTool(headers={'User-Agent': random.choice(USER_AGENTS)}),
                YutoriNewsTool(),
                SEC10QTool(),
                SEC10KTool(),
            ]
        )
    
    @task
    def research(self) -> Task:
        return Task(
            config=self.tasks_config['research'],
            agent=self.research_analyst_agent(),
        )
    
    @agent
    def financial_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'],
            verbose=True,
            llm=llm,
            tools=[
                ScrapeWebsiteTool(headers={'User-Agent': random.choice(USER_AGENTS)}),
                CalculatorTool(),
                SEC10QTool(),
                SEC10KTool(),
            ]
        )
    
    @task
    def financial_analysis(self) -> Task: 
        return Task(
            config=self.tasks_config['financial_analysis'],
            agent=self.financial_analyst_agent(),
        )
    
    @task
    def filings_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['filings_analysis'],
            agent=self.financial_analyst_agent(),
        )

    @agent
    def investment_advisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['investment_advisor'],
            verbose=True,
            llm=llm,
            tools=[
                ScrapeWebsiteTool(headers={'User-Agent': random.choice(USER_AGENTS)}),
                CalculatorTool(),
            ]
        )

    @task
    def recommend(self) -> Task:
        return Task(
            config=self.tasks_config['recommend'],
            agent=self.investment_advisor_agent(),
        )
    
    
    @crew
    def crew(self) -> Crew:
        """Creates the Stock Analysis"""
        return Crew(
            agents=self.agents,  
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "ollama",
                "model_name": "nomic-embed-text",
                "url": "http://localhost:11434/api/embeddings"
            }
        )
