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



st.set_page_config(page_title="Catalyst Agent", layout="wide")
st.title("AI Skill Assessment & Learning Plan Agent")

# Session State Management
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

# Phase 1: Upload & Extraction
if st.session_state.phase == "upload":
    with st.form("upload_form"):
        st.subheader("1. Upload Details")
        jd_input = st.text_area("Paste Job Description Here", height=170)
        resume_upload = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        submit_btn = st.form_submit_button("Start Assessment")

    if submit_btn and jd_input and resume_upload:
        with st.spinner("Analyzing Resume against the job description..."):
            resume_text = extract_text_from_pdf(resume_upload)
            analysis = extract_skills_and_gaps(resume_text, jd_input)
            
            st.session_state.initial_gaps = analysis['initial_gaps']
            # We will only test the skills they claim to have that match the JD requirements
            st.session_state.skills_to_test = [skill for skill in analysis['claimed_skills'] if skill in analysis['required_skills']]
            
            if not st.session_state.skills_to_test:
                #Asks about the first 3 skills required in JD if no skills match
                st.session_state.skills_to_test = analysis['required_skills'][:3] 
                
            # Generate the first question
            first_skill = st.session_state.skills_to_test[0]
            st.session_state.current_question = generate_interview_question(first_skill, jd_input)
            st.session_state.chat_history.append({"role": "assistant", "content": st.session_state.current_question})
            st.session_state.jd_input = jd_input # saving for later purpose
            
            st.session_state.phase = "assessment"
            st.rerun()

# Phase 2: Assessment Loop
elif st.session_state.phase == "assessment":
    current_skill = st.session_state.skills_to_test[st.session_state.current_skill_index]
    
    st.subheader(f"Skill Assessment: {current_skill.upper()}")
    st.progress((st.session_state.current_skill_index) / len(st.session_state.skills_to_test))

    # Render chat history
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if user_answer := st.chat_input("Your answer..."):
        # Append user answer
        st.session_state.chat_history.append({"role": "user", "content": user_answer})
        st.chat_message("user").write(user_answer)
        
        with st.spinner("Evaluating answer..."):
            # Evaluate the answer provided by the user
            evaluation = evaluate_answer(
                skill=current_skill, 
                question=st.session_state.current_question, 
                answer=user_answer
            )
            
            if not evaluation['passed']:
                st.session_state.failed_skills.append(current_skill)
                
            # Provide feedback in chat
            feedback_msg = f"**Feedback (Score: {evaluation['score']}/5):** {evaluation['feedback']}"
            st.session_state.chat_history.append({"role": "assistant", "content": feedback_msg})
            st.chat_message("assistant").write(feedback_msg)
            
            # Move to next skill or finish
            st.session_state.current_skill_index += 1
            
            if st.session_state.current_skill_index < len(st.session_state.skills_to_test):
                next_skill = st.session_state.skills_to_test[st.session_state.current_skill_index]
                time.sleep(1) 
                next_question = generate_interview_question(next_skill, st.session_state.jd_input)
                st.session_state.current_question = next_question
                st.session_state.chat_history.append({"role": "assistant", "content": next_question})
                st.rerun()
            else:
                st.success("Assessment Complete! Generating your learning plan...")
                time.sleep(2)
                st.session_state.phase = "plan"
                st.rerun()

#  Phase 3: Learning Plan Generation
elif st.session_state.phase == "plan":
    st.subheader("Here is your Personalized Learning Plan")
    
    with st.spinner("Compiling resources and estimates..."):
        final_plan = generate_learning_plan(
            st.session_state.failed_skills, 
            st.session_state.initial_gaps
        )
        st.markdown(final_plan)
        
        if st.button("Start Over"):
            st.session_state.clear()
            st.rerun()