from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import TypedDict,Annotated
import operator

load_dotenv(

)

model = ChatOpenAI(model="gpt-4o-mini")

class EvaluationSchema(BaseModel):
    feedback:str = Field(...,description="The FeedBack for the Easy")
    score:int = Field(...,description="The Score for the Easy",gt=0,lt=11)

structured_output = model.with_structured_output(EvaluationSchema)

essay = """The pyramids are among the most fascinating and enduring structures ever created by human civilization. Built thousands of years ago, they continue to capture the imagination of historians, archaeologists, and travelers from around the world. These monumental structures are most famously associated with ancient Egypt, where they served as tombs for pharaohs and symbols of power, religion, and advanced engineering.

The most well-known pyramids are located in Giza Pyramid Complex, near the city of Cairo. Among them stands the Great Pyramid of Giza, which is considered one of the Seven Wonders of the Ancient World. It was built for the Pharaoh Khufu around 4,500 years ago. This pyramid originally stood about 146 meters tall and was constructed using millions of limestone blocks, each weighing several tons."""

prompt = f"Evaluate the following essay on a scale of 1 to 10, where 1 is the lowest and 10 is the highest. Provide feedback on the strengths and weaknesses of the {essay}."
r = structured_output.invoke(prompt)
print(r)

class AISTATE(TypedDict):
    essay:str
    grammer_feedback:str
    analysis_feedback:str
    COT_Feedback:str
    overall_feedback:str
    individual_scores:Annotated[list[int],operator.add]
    avg_score:float


def  evaluate_grammer (state:AISTATE)->AISTATE:
    prompt =f"Evaluate the grammar of the following essay and provide feedback: {state['essay']}"
    model_1 = structured_output.invoke(prompt)
    return {"grammer_feedback":model_1.feedback,"individual_scores":[model_1.score]}

def  evaluate_analysis (state:AISTATE)->AISTATE:
    prompt =f"Evaluate the analysis of the following essay and provide feedback: {state['essay']}"
    model_1 = structured_output.invoke(prompt)
    return {"analysis_feedback":model_1.feedback,"individual_scores":[model_1.score]}

def  evaluate_thought (state:AISTATE)->AISTATE:
    prompt =f"Evaluate the clarity of thought of the following essay and provide feedback: {state['essay']}"
    model_1 = structured_output.invoke(prompt)
    return {"COT_Feedback":model_1.feedback,"individual_scores":[model_1.score]}

def  final_eval (state:AISTATE)->AISTATE:
    prompt = f"based on the following feedback, provide an overall evaluation of the essay: Grammar Feedback: {state['grammer_feedback']}, Analysis Feedback: {state['analysis_feedback']}, Clarity of Thought Feedback: {state['COT_Feedback']}. Also, calculate the average score based on the individual scores provided.",
    answer = model.invoke(prompt).content
    sum_of_scores = sum(state['individual_scores'])
    average_score = sum_of_scores / len(state['individual_scores']) if state['individual_scores'] else 0
    return {"overall_feedback":answer, "avg_score":average_score}

graph = StateGraph(AISTATE)

graph.add_node("evaluate_grammer",evaluate_grammer)
graph.add_node("evaluate_analysis",evaluate_analysis)
graph.add_node("evaluate_thought",evaluate_thought)
graph.add_node("final_eval",final_eval)

graph.add_edge(START,"evaluate_grammer")
graph.add_edge(START,"evaluate_analysis")
graph.add_edge(START,"evaluate_thought")
graph.add_edge("evaluate_grammer","final_eval")
graph.add_edge("evaluate_analysis","final_eval")
graph.add_edge("evaluate_thought","final_eval")
graph.add_edge("final_eval",END)

work_flow = graph.compile()

init_state = {"essay":essay}

result = work_flow.invoke(init_state)
print(result)