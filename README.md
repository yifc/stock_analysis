# Personal Investment Advisor 🤖📈

An autonomous, privacy-first AI agent crew for deep stock market analysis. Built with [CrewAI](https://crewai.com), this project orchestrates a team of specialized AI agents to research, analyze, and recommend investment strategies—all running 100% locally to ensure data privacy.

## Features

- **🔒 Privacy-First Architecture**: Runs entirely on your machine using **Ollama** with `llama3.1` (logic) and `nomic-embed-text` (memory). No sensitive financial data leaves your local environment.
- **🔄 Continuous Intelligence**: Features a **ScoutMonitor** (powered by Yutori) that watches for real-time news and market events, automatically triggering the crew to re-analyze when significant updates occur.
- **🧠 Event-Driven Memory**: Includes a `StockMemoryListener` that logs memory operations, allowing agents to retain context across tasks and better "reason" about data.
- **📊 Comprehensive Analysis**:
  - **Research Analyst**: Scours the web for sentiment and news.
  - **Financial Analyst**: Parses complex SEC 10-K/10-Q filings for hard financial data.
  - **Investment Advisor**: Synthesizes all data into actionable recommendations.

## Prerequisites

Before running, ensure you have the following installed:

1.  **Python >=3.12**
2.  **[Poetry](https://python-poetry.org/)** for dependency management.
3.  **[Ollama](https://ollama.com/)** for local LLM inference.

### setting up Ollama

You need to pull the specific models used by the crew:

```bash
ollama pull llama3.1
ollama pull nomic-embed-text
```

Ensure Ollama is running in the background (`ollama serve`).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd stock_analysis
    ```

2.  **Install dependencies**:
    ```bash
    poetry install
    ```

3.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your keys:
    ```bash
    cp .env.example .env
    ```
    Required keys:
    - `OPENAI_API_KEY` (Not used by default since we use Ollama, but kept for compatibility)
    - `YUTORI_API_KEY` (For the ScoutMonitor news tool)
    - `SERPER_API_KEY` (For Google Search via Serper)
    - `SEC_API_API_KEY` (For SEC filings)

## Usage

To start the crew:

```bash
poetry run stock_analysis
```

### Interactive Flow
1.  **Enter Company**: You will be prompted to enter a stock ticker (e.g., `AAPL`, `TSLA`).
2.  **Continuous Monitoring**: You'll be asked if you want to enable continuous monitoring (`y/n`).
    - **No**: Runs a one-time analysis and exits.
    - **Yes**: Runs an initial analysis, then starts the `ScoutMonitor`. The script will keep running, and if the Yutori scout detects new relevant news, the crew will automatically wake up and generate an updated report.

## Customization

- **Agents**: Modify `src/stock_analysis/config/agents.yaml` to tweak agent personas.
- **Tasks**: Modify `src/stock_analysis/config/tasks.yaml` to change the analysis workflow.
- **Logic**: Check `src/stock_analysis/crew.py` to see how agents are wired together.

## License
MIT
