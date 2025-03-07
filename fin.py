from phi.agent import Agent
from phi.agent import Agent, RunResponse
from phi.model.google import Gemini
from phi.tools.yfinance import YFinanceTools

finance_agent = Agent(
    name="Finance Agent",
    model=Gemini(id="gemini-1.5-flash"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)
finance_agent.print_response("Give me entire summry of NVDIA Share", stream=True)