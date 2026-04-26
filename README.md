# Catalyst: AI Skill Assessment & Learning Plan Agent 🚀

**Catalyst** is an AI-powered technical recruiter and mentor. It solves a critical hiring problem: *a resume tells you what someone claims to know, not how well they actually know it.* This agent takes a Job Description and a candidate's resume, assesses real proficiency on each required skill through a conversational interview, identifies gaps, and generates a highly personalized, actionable learning plan.

Built for the Deccan AI Hackathon 2026 .

### 🔗 Important Link
* **Live Web App:** [(https://catalyst-skill-assessment-agent.streamlit.app/)]


---

## ✨ Key Features
1. **Intelligent Gap Analysis:** Cross-references resume claims with job requirements using strict JSON-schema extraction.
2. **Dynamic Scenario Interviews:** Generates practical, scenario-based questions rather than asking for rote definitions.
3. **Objective Evaluation:** Acts as a strict technical interviewer to grade responses (0-5 scale) and provide immediate feedback.
4. **Curated Learning Plans:** Compiles failed skills and initial gaps into a structured Markdown study guide with time estimates and free resources.

---

## 🧠 Architecture & Logic

```mermaid
graph TD
    A[User Input: Streamlit UI] --> B[PDF Parsing: PyPDF2 / text extraction]
    A --> C[Job Description Text]
    B --> D(Agent 1: Extraction)
    C --> D
    D -->|Identifies claimed skills & gaps| E(Agent 2: Question Generation)
    E -->|Asks scenario-based question| F[User Answers in Chat]
    F --> G(Agent 3: Evaluation)
    G -->|Returns Score, Feedback, Pass/Fail| H{More skills to test?}
    H -->|Yes| E
    H -->|No: Compiles failed skills| I(Agent 4: Learning Plan)
    I --> J[Final Output: Personalized Markdown Study Guide]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    style J fill:#bbf,stroke:#333,stroke-width:2px,color:#000
```
Core Logic & State Management:
The application's "brain" relies on strict structural enforcement and persistent state tracking. To prevent the LLM from returning unpredictable conversational text, the backend utilizes Pydantic schemas paired with the LLM's JSON response formatting. This forces the agents to output highly reliable, validated JSON objects (e.g., specific lists of missing skills, or integer scores and boolean pass/fail flags) that the Python backend can programmatically parse.

To handle the conversational interview experience, the frontend leverages Streamlit's session_state. Because Streamlit reruns the entire script upon every user interaction, session_state is used as the application's short-term memory. It securely preserves the chat history, tracks the index of the current skill being tested, and aggregates the initial resume gaps alongside the skills failed during the interview, passing the complete list to the final agent to generate the learning plan.

---
 
## 🖥️ Running Locally
 
### Prerequisites
- Python 3.9 or higher
- Google API key 
### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/catalyst-skill-assessment-agent.git]
cd catalyst-skill-assessment-agent
```
 
### 2. Create & Activate a Virtual Environment
```bash
# Create the environment
python -m venv venv
 
# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```
 
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
 
### 4. Set Up Your API Key
Create a `.env` file in the root of the project and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```
> ⚠️ Never commit your `.env` file. Make sure it's listed in `.gitignore`.
 
### 5. Run the App
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.
 
---
