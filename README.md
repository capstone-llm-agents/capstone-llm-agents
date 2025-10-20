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

## Prerequisites
Before you begin, ensure you have the following installed on your system.
1. Python
   * **Requirement:** ```Python 3.13``` 
   * **Installation:** Can be downloaded from https://www.python.org/downloads/

2. Python Package Manager
   You will need a python package manager to be able to install all the necessary packages. You can either use ```Pip``` or ```uv```
      * ```Pip```: This is the standard package manager and comes included with python and so no separate installation is needed. 
      * ```uv```**(Recommended):** uv is a much faster alternative to pip, and its much easier to use.
        * **Installation:** can be installed from https://docs.astral.sh/uv/getting-started/installation/

3. Ollama and a Local LLM model
   This project by default uses local model through Ollama.
   * **Install Ollama:** Download the application from https://ollama.com/.
   * **Download Gemma3 & mxbai-embed-large:** After installing ```Ollama``` open your terminal and run ```ollama pull gemma3``` to download Gemma3 and ```ollama pull mxbai-embed-large``` to download mxbai-embed-large.

    **Note:** The application can also be configured to use other model providers like ```OpenAI``` please refer to the **Configuration** section for more details.

## Installation
Start by cloning the repository or downloading it from here and navigate to the main project directory which would be under ```/capstone-llm-agents``` and open a terminal window.
### Using Pip
1. Start by creating a virtual environment using ```python -m venv .venv```.
2. Then on linux or macOS run ```source .venv/scripts/activate``` to enter the virtual environment or on windows run  ```.venv/scripts/activate```.
   On windows if you get an ExecutionPolicy error run this command first ```Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser```.
3. Then run ```pip install -r requirements.txt``` to install all the necessary packages for this project.
### Using uv
1. Run ```uv sync``` to create a virtual environment and install all the necessary packages. 

## Running the Application
1. Navigate to the project directory and open a terminal windows. 
2. Make sure all the packages are installed refer to the instructions above for that.
3. If you are using ```ollama``` then make sure you have pulled ```gemma3``` and make sure ```ollama``` is running. If you're not using ```ollama``` skip this step
4. Then in the terminal window:
   * If your using ```pip``` activate the virtual environment ```source .venv/scripts/activate``` on Linux and macOs or ```.venv\Scripts\Activate.ps1``` on Windows and run ```honcho start``` which will run all      the necessary servers and startup the application.
   * If your using ```uv``` run ```uv run honcho start```.

   
**Note** if your using linux or mac some shells require a different activatation script, for example using ```fish``` its ```.venv/bin/activate.fish```

## Extra Information 
The ```honcho start``` command starts four different servers, and they are in no particular oder:
1. A mcp server for a weather tool.
2. A mcp server for a calendar tool.
3. A mcp server for a pdf tool.
4. A websocket server for user authentication and networking between several clients.

When the application starts:
- If the network server is running, you'll see a login/signup screen
- You can log in with existing credentials or create a new account
- If the server is not running, you can click "Skip (Offline Mode)" to continue without network features
**Note:** Network features include friend management, agent discovery, and cross-user messaging. In offline mode, these features will not be available.
The application comes with these test users:
     - Username: `alice`, Password: `password123`
     - Username: `bob`, Password: `password123`
     - Username: `charlie`, Password: `password123`
You can also create new users through the signup screen.
       
### Configuration

**Note** OpenAI API key variable names must be ```OPENAI_API_KEY``` and Google API key must be ```GEMINI_KEY```.
#### Windows
On windows, we can set a **temporary** environment using ```set VARIABLE_NAME=value``` in command prompt and ``$env:VARIABLE_NAME=value`` in Windows PowerShell, for example to set an OpenAI API key it would be something like ```set OPENAI_API_KEY=sk-.....``` in cmd or ```$env:OPENAI_API_KEY=sk-...``` .
To set a permanent environment variable follow the following steps:
1. Search for **Edit the system environment variables** in the search bar and open the first match.
2. In the opened window click on the **Environment variables** on the bottom right.
3. In the **User Variables for user** tab click on the **New** button and enter the variable name which would be the API Key Name and the varaiable value would be the API Key itself.
[For more information visit](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables?view=powershell-7.5)

#### Mac
On Mac we first need to identify which shell your running this can be done by doing ```echo $$SHELL``` in terminal which should print out the shell you are using.
The default shell on modern Mac computers is **Zsh**, older Macs might be using **Bash**.
1. For **Zsh** you need to open the ```~/.zshrc``` file using a text editor of your choice, but the simplest way is using nano by running ```nano ~/.zshrc``` and adding a variable in the file with ```export VARIABLE_NAME="variable-value"```, for example for an OpenAI API key it would be ```export OPENAI_API_KEY="sk-...."```.
2. For **Bash** you need to open the ```~/.bash_profile``` file using a text editor of your choice and follow the same steps as for **Zah**.

#### Linux
On Linux similar to Mac we first need to identify which shell your running this can be done by doing ```echo $$SHELL``` in terminal which should print out the shell you are using.
for **Bash** and **Zsh** it's the same process, but there are a lot of shells available on linux so you need to research the specific shell you are using.

### Choosing a model
After setting up your api keys as environment variables, navigate to the project directory and open the subdirectory called ```config```
in that directory open the file named ```models.yaml```, there you will be met with the following:
```yaml
default_embedding_model: 0
default_model: 2
default_model_with_native_tools: 1
default_powerful_model: 2
default_quick_model: 3
default_local_model: 0
default_super_quick_model: 3
embedding_models:
  - model: mxbai-embed-large
    provider: ollama
  - model: nomic-embed-text
    provider: ollama
models:
  - model: gemma3
    provider: ollama
  - model: llama3.2
    provider: ollama
  - model: gpt-4o-mini
    provider: openai
  - model: gemma3:1b
    provider: ollama
version: "1.0"
```
For the most part you will just need to change the ```default_model:``` for the application to work better since the local embedding models are powerful enough for this application.


