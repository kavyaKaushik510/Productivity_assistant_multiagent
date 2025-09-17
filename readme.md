# Productivity Planning Agent (Multi-Agent System)

This project is a **multi-agent productivity assistant** built using **LangGraph** and **LangChain**.  
It integrates with **Gmail, Google Docs, and Google Calendar** to automatically extract, prioritise, and schedule tasks.


## Features
- **Email Manager**: Classifies incoming emails, summarises important ones, and extracts actionable tasks.  
- **Meeting Summariser**: Summarises Google Docs meeting notes and extracts tasks assigned to the user.  
- **Task Prioritiser**: Applies rule-based logic to assign HIGH, MED, or LOW priorities based on deadlines and keywords.  
- **Calendar Optimiser**: Fetches events from Google Calendar and proposes free time blocks for pending tasks.  

## Architecture
- Agents are orchestrated using **LangGraph**.  
- Communication is handled via **dict-based state passing** with Pydantic schemas (`Task`, `Summary`, `CalendarResult`).  
- External APIs:
  - **Gmail API** – fetch raw emails  
  - **Google Docs API** – fetch meeting notes  
  - **Google Calendar API** – fetch and propose time slots  
  - **LLM (Gemini / OpenAI)** – summarisation and task extraction  

---

## How to Run

1. **Clone the repo and install requirements**  
   ```bash
   git clone https://github.com/kavyaKaushik510/Productivity_assistant_multiagent.git
   pip install -r requirements.txt

2. **Run the final pipeline**
   ```bash
   python -m tests.test_pipeline
   sample_output.txt contains an example of a run setup
  
   
