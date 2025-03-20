
from langchain.llms import Gemini
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from typing import Dict, TypedDict
import os, requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = Gemini(api_key=GEMINI_API_KEY)

# Define state structure
class AgentState(TypedDict):
    topic: str
    questions: list
    llm_answers: list
    web_answers: list
    final_answers: list
    document: str

# Prompts
question_prompt = PromptTemplate(
    input_variables=["topic"],
    template="Generate 10 detailed, foundational questions about {topic} that require in-depth answers.These answers should be separated by newlines. No need to generate anything else, just the questions."
)
answer_prompt = PromptTemplate(
    input_variables=["question"],
    template="Provide a detailed answer (3-5 paragraphs) to this question: {question}. Include examples and explanations."
)

# Node functions
def generate_questions(state: AgentState) -> AgentState:
    questions = llm(question_prompt.format(topic=state["topic"])).split("\n")
    state["questions"] = [q.strip() for q in questions if q.strip()]
    return state

def generate_answers(state: AgentState) -> AgentState:
    state["llm_answers"] = [llm(answer_prompt.format(question=q)) for q in state["questions"]]
    return state

def fetch_wikipedia_summary(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("extract", "No summary found.")
        return "No summary found."
    except:
        return "No summary found."

def fetch_web_answers(state: AgentState) -> AgentState:
    state["web_answers"] = [fetch_wikipedia_summary(q.split()[-1]) for q in state["questions"]]
    return state

def refine_answers(state: AgentState) -> AgentState:
    final_answers = []
    for q, llm_ans, web_ans in zip(state["questions"], state["llm_answers"], state["web_answers"]):
        if "No summary found" in web_ans:
            final_answers.append(llm_ans)
        else:
            final_answers.append(f"{llm_ans}\n\n**Additional Context from Web:**\n{web_ans}")
    state["final_answers"] = final_answers
    return state

def compile_document(state: AgentState) -> AgentState:
    doc = f"# In-Depth Guide to {state['topic']}\n\nThis document provides detailed insights into {state['topic']}.\n\n"
    for q, a in zip(state["questions"], state["final_answers"]):
        doc += f"## {q}\n{a}\n\n"
    state["document"] = doc
    return state

# Build the agent graph
workflow = StateGraph(AgentState)
workflow.add_node("generate_questions", generate_questions)
workflow.add_node("generate_answers", generate_answers)
workflow.add_node("fetch_web_answers", fetch_web_answers)
workflow.add_node("refine_answers", refine_answers)
workflow.add_node("compile_document", compile_document)

workflow.add_edge("generate_questions", "generate_answers")
workflow.add_edge("generate_answers", "fetch_web_answers")
workflow.add_edge("fetch_web_answers", "refine_answers")
workflow.add_edge("refine_answers", "compile_document")
workflow.add_edge("compile_document", END)

workflow.set_entry_point("generate_questions")
agent = workflow.compile()