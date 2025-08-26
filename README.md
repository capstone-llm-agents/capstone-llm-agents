# Capstone Project ID 33 - Multi-Agent systems with LLM-based agents

## Team members:
- Anton Chuchuva - 104584362@student.swin.edu.au
- Adrien Krebet - 104546906@student.swin.edu.au
- Chao-Ming Wang - 101100545@student.swin.edu.au
- Joel Downie - 104540652@student.swin.edu.au
- Aqeel Safdari - 104006248@student.swin.edu.au
- Ned Olsen - 104544609@student.swin.edu.au

## Project Description:
Intelligent agent technology is an important artificial intelligent (AI) paradigm aiming to develop AI systems that can operate successfully in a task environment to achieve beneficial outcomes. In recent years, Large Language models (LLMs) has become a significant advancement in AI technologies to achieve some important capabilities in natural language understanding and generation and problem solving. Thus, it’s natural to consider LLM as the engine to build powerful intelligent agents. On the other hand, enhancing current LLMs with the intelligent agent’s capabilities of sensing and acting can significantly extend their versatility and applicability in many important applications. This project focuses on building a prototype for multiagent systems consisting of multiple LLM-based agents who can cooperate to work on tasks that require different agents with different capabilities and knowledge bases to jointly arrive at a solution to the problem or a joint plan to achieve common goals.

## Installation

Install ```uv``` from ```https://docs.astral.sh/uv/getting-started/installation/```

Download ```Ollama``` from ```https://ollama.com/```.

Choose a model to install via ```ollama pull <model_name>```. ```ollama pull gemma3``` is recommended.

Clone the repository.

Install Python 3.13 with ```uv python install 3.13```

Run ```uv venv``` to create the virtual environment.

Run ```source .venv/bin/activate``` to run the virtual environment.

Run ```uv sync``` to install the packages.

## Running the Project

```python main.py```

## Running a Script

Running a script in the scripts folder called "script_name". Replace with the actual name of the script you want to run.

```python -m scripts.script_name```

For example if I have a script called "test_actions.py", "script_name" would be "test_actions".

```python -m scripts.test_actions```

## Running MCP servers

For some of the agents, they need their tools to work better, or work at all.

These servers are found in the ```mcp_server``` directory.

Run them with ```python ./mcp_server/<server_file_name>```

For example, ```python ./mcp_server/calendar_server.py``` to run the server with the calendar tools.

The application also supports external servers you can add them through the GUI. Currently it doesn't support headers, so most servers don't work. This will be fixed later on.