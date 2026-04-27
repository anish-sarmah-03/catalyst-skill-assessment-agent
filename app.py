import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils import extract_text_from_pdf
from agents import (
    extract_skills_and_gaps, 
    generate_interview_question, 
    evaluate_answer, 
    generate_learning_plan
)
import time

st.set_page_config(
    page_title="Catalyst | Skill Agent", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #4A90E2;
        margin-bottom: 0px;
    }
    .sub-text {
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown('<p class="main-header">Catalyst: AI Skill Assessment & Learning Plan Agent 🚀</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Validate claims. Discover gaps. Build personalized learning paths.</p>', unsafe_allow_html=True)
st.divider()

#  Session State Management 
if "phase" not in st.session_state:
    st.session_state.phase = "upload" 
if "skills_to_test" not in st.session_state:
    st.session_state.skills_to_test = []
if "current_skill_index" not in st.session_state:
    st.session_state.current_skill_index = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "failed_skills" not in st.session_state:
    st.session_state.failed_skills = []
if "initial_gaps" not in st.session_state:
    st.session_state.initial_gaps = []
if "current_question" not in st.session_state:
    st.session_state.current_question = ""


with st.sidebar:
    st.header("⚙️ Dashboard")
    if st.session_state.phase == "upload":
        st.info("Upload a candidate's resume and the target job description to begin the automated screening.")
    elif st.session_state.phase == "assessment":
        st.success(f"Testing {len(st.session_state.skills_to_test)} matching skills.")
        st.progress((st.session_state.current_skill_index) / len(st.session_state.skills_to_test))
        st.write(f"**Current Skill:** {st.session_state.skills_to_test[st.session_state.current_skill_index]}")
    elif st.session_state.phase == "plan":
        st.success("Assessment complete! View the generated learning plan.")


# Phase 1: Upload & Extraction
if st.session_state.phase == "upload":
    st.markdown("### 📄 Setup Candidate Assessment")
    
    with st.form("upload_form", border=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**1. Target Job Description**")
            jd_input = st.text_area("Paste the requirements here:", height=200, placeholder="e.g. Seeking a Machine Learning Engineer proficient in Python, PyTorch, and Docker...")
        
        with col2:
            st.markdown("**2. Candidate Resume**")
            resume_upload = st.file_uploader("Upload PDF file", type=["pdf"])
            st.caption("Only PDF format is currently supported.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 Start AI Assessment", use_container_width=True)

    if submit_btn and jd_input and resume_upload:
        with st.status("🧠 Processing Data...", expanded=True) as status:
            st.write("Extracting text from PDF...")
            resume_text = extract_text_from_pdf(resume_upload)
            
            st.write("Cross-referencing skills with Job Description...")
            analysis = extract_skills_and_gaps(resume_text, jd_input)
            
            st.session_state.initial_gaps = analysis['initial_gaps']
            st.session_state.skills_to_test = [skill for skill in analysis['claimed_skills'] if skill in analysis['required_skills']]
            
            if not st.session_state.skills_to_test:
                st.session_state.skills_to_test = analysis['required_skills'][:3] 
                
            st.write("Generating dynamic interview environment...")
            first_skill = st.session_state.skills_to_test[0]
            st.session_state.current_question = generate_interview_question(first_skill, jd_input)
            st.session_state.chat_history.append({"role": "assistant", "content": st.session_state.current_question})
            st.session_state.jd_input = jd_input 
            
            status.update(label="Analysis Complete!", state="complete", expanded=False)
            time.sleep(1)
            st.session_state.phase = "assessment"
            st.rerun()

# Phase 2: Assessment Loop 
elif st.session_state.phase == "assessment":
    current_skill = st.session_state.skills_to_test[st.session_state.current_skill_index]
    
  
    st.markdown(f"### 🎯 Active Test: `{current_skill.upper()}`")
    st.caption("Answer the scenario-based question below. The AI will evaluate your practical proficiency.")
    st.divider()

  
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if user_answer := st.chat_input("Type your solution here..."):
        st.session_state.chat_history.append({"role": "user", "content": user_answer})
        st.chat_message("user").write(user_answer)
        
        with st.spinner("🤖 Grading response..."):
            evaluation = evaluate_answer(
                skill=current_skill, 
                question=st.session_state.current_question, 
                answer=user_answer
            )
            
            if not evaluation['passed']:
                st.session_state.failed_skills.append(current_skill)
                feedback_color = "red"
                status_icon = "❌"
            else:
                feedback_color = "green"
                status_icon = "✅"
                
           
            feedback_msg = f"{status_icon} **Score: {evaluation['score']}/5** \n\n {evaluation['feedback']}"
            st.session_state.chat_history.append({"role": "assistant", "content": feedback_msg})
            st.chat_message("assistant").write(feedback_msg)
            
            st.session_state.current_skill_index += 1
            
            if st.session_state.current_skill_index < len(st.session_state.skills_to_test):
                next_skill = st.session_state.skills_to_test[st.session_state.current_skill_index]
                time.sleep(1.5) 
                next_question = generate_interview_question(next_skill, st.session_state.jd_input)
                st.session_state.current_question = next_question
                st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                st.rerun()
            else:
                st.balloons()
                st.success("🎉 Assessment Complete! Generating your learning plan...")
                time.sleep(3)
                st.session_state.phase = "plan"
                st.rerun()

# Phase 3: Learning Plan Generation 
elif st.session_state.phase == "plan":
    st.markdown("### 📚 Your Personalized Growth Plan")
    st.info("Based on your resume gaps,  and interview performance, we've curated this syllabus for you.")
    
    with st.spinner("Compiling resources and estimates..."):
        final_plan = generate_learning_plan(
            st.session_state.failed_skills, 
            st.session_state.initial_gaps
        )
        
        with st.container(border=True):
            st.markdown(final_plan)
        
        st.divider()
        if st.button("🔄 Assess Another Candidate", type="primary"):
            st.session_state.clear()
            st.rerun()
