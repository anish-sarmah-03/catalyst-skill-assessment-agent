import google.generativeai as genai                  #To commumicate with Gemini model
import os                                              #To securely read env variables
from pydantic import BaseModel   #To let the AI know what format to return the answers
from typing import List                  #To specify that certain fields will be Lists


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')    #This model has been chosen as it is fast, cost-effective, and  highly capable of structured tasks.

#  Schemas for Structured Output 
class ExtractionResult(BaseModel):
    claimed_skills: List[str]
    required_skills: List[str]
    initial_gaps: List[str]

class EvaluationResult(BaseModel):
    score: int
    feedback: str
    passed: bool

# Agent Functions 

#Agent function 1(Extracting skills from resume and comparing with job description):
def extract_skills_and_gaps(resume_text: str, jd_text: str) -> dict:
    """Compares the resume against the JD and extracts skills and initial gaps."""
    prompt = f"""
    You are an expert technical recruiter. 
    Compare the following Resume to the Job Description.
    Identify the skills the candidate claims to have, the core skills required as per the job description, 
    and the skills required for the job but missing from the resume.
    
    Resume: {resume_text}
    Job Description: {jd_text}
    """
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ExtractionResult,
            temperature=0.1,
        ),
    )


    import json
    return json.loads(response.text)

#Agent function 2(Generating interview questions):
def generate_interview_question(skill: str, jd_context: str) -> str:
    """Generates a practical, scenario-based question for a specific skill."""
    prompt = f"""
    You are a technical interviewer assessing a candidate for a role.
    Generate ONE practical, scenario-based interview question to test the candidate's 
    actual proficiency in the skill: '{skill}'.
    Context from the job description: {jd_context}
    
    Do not ask definitions. Ask how they would solve a problem using this skill.
    Output only the question.
    Try to use skills section from resume also and ask questions related to it.
    Also, you can ask some questions based on the projects written in resume.
    If the candidate fails to answer, try asking a quite simpler(not very easy) question .
    Important Note: If the user does not have any work experience section, don't ask many questions on the applications. You may ask a few technical questions based on skills provided, e.g. 1-2 DSA questions , 1-2 oops questions for SDE role etc.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt, 
                generation_config=genai.GenerationConfig(temperature=0.7)
            )
            return response.text
        
        except ResourceExhausted:
            print(f"Rate limit hit. Sleeping for 30 seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(30)
            
    
    return "Error: Could not generate question due to continuous API limits."

#Agent function 3(Evaluating the answers):
def evaluate_answer(skill: str, question: str, answer: str) -> dict:
    """Evaluates the user's answer and determines if they actually know the skill."""
    prompt = f"""
    You are a strict technical interviewer. Evaluate the candidate's answer.
    Skill being tested: {skill}
    Question asked: {question}
    Candidate's Answer: {answer}
    
    Score the answer from 0 to 5, based on the candidate's answer. 
    Provide brief feedback.
    Determine if they passed the test(score >= 3).
    """
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=EvaluationResult,
            temperature=0.1,
        ),
    )
    import json
    return json.loads(response.text)


#Agent function 4(Generating personalised learning plan):

def generate_learning_plan(failed_skills: list, initial_gaps: list) -> str:
    """Creates a curated learning plan based on all identified gaps."""
    all_gaps = list(set(failed_skills + initial_gaps))
    
    prompt = f"""
    You are a career guide. The candidate lacks practical proficiency in these areas: {', '.join(all_gaps)}.
    Generate a personalized, highly structured Markdown learning plan to acquire these skills.
    For each skill, include:
    - Why it's important.
    - 2-3 specific, high-quality free resources (e.g., specific YouTube channels, official docs, blogs etc.).
    - A realistic estimated time (in hours) to acquire foundational proficiency.
    At the end, provide some motivational text so that the candidate does not feel under confident.
    
    """
    response = model.generate_content(prompt, generation_config=genai.GenerationConfig(temperature=0.4))
    return response.text