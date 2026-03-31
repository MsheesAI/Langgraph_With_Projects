from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field 
from typing import TypedDict,Annotated,Literal
import operator
import json
load_dotenv(

)

model = ChatOpenAI(model="gpt-4o-mini")

class SentimentSchema(BaseModel):
    sentiment:str = Field(...,description="The sentiment of the review")

class DiagnosisSchema(BaseModel):
    issue_type:Literal["billing","product","service","Other"] = Field(...,description="The type of issue mentioned in the review")
    tone:Literal["friendly","formal","casual","very angry"] = Field(...,description="The tone of the review")
    urgency:Literal["low","medium","high"] = Field(...,description="The urgency level of the issue mentioned in the review")

structured_model = model.with_structured_output(SentimentSchema)
prompt = "What is the sentiment of the following review: 'The movie was fantastic and I loved it!'?"
r = structured_model.invoke(prompt)
print(r)

structured_model2 = model.with_structured_output(DiagnosisSchema)

class ReviewState(TypedDict):
    review:str
    sentiment:Literal["positive","negative","neutral"]
    diagnosis:dict
    response:str



def find_sentiment(state:ReviewState)->ReviewState:
    prompt = f"For the following review, determine the sentiment (positive, negative, or neutral): {state['review']}"
    sentiment = structured_model.invoke(prompt).sentiment
    return {"sentiment":sentiment}

def check_sentiment(state:ReviewState)->Literal["positive_response","run_diagnosis"]:
    if state['sentiment'] == "positive":
        return "positive_response"
    else:
        return "run_diagnosis"
    
def positive_response(state:ReviewState)->ReviewState:
    prompt = f"write a warm thankyou message in response to this state ${state["review"]} and also said to give feedback on our site",
    response = model.invoke(prompt).content
    return {"response":response}
def run_diagnosis(state:ReviewState)->ReviewState:
    prompt = f"write a diagnostic message in response to this state ${state['review']} Return issue type,tone,and urgency",
    response = structured_model2.invoke(prompt)
    return {"diagnosis":response.model_dump()}
def negative_response(state:ReviewState)->ReviewState:
    diagnosis = state["diagnosis"]
    prompt = f"the user had a {diagnosis['issue_type']} issue sounded {diagnosis['tone']} and had an urgency level of {diagnosis['urgency']}. Write a response to the user addressing their concerns and offering assistance.",
    response = model.invoke(prompt).content
    return {"response":response}

graph = StateGraph(ReviewState)
graph.add_node("find_sentiment",find_sentiment)
graph.add_node("positive_response",positive_response)
graph.add_node("run_diagnosis",run_diagnosis)
graph.add_node("negative_response",negative_response)

graph.add_edge(START,"find_sentiment")
graph.add_conditional_edges("find_sentiment",check_sentiment)
graph.add_edge("positive_response",END)
graph.add_edge("run_diagnosis","negative_response")
graph.add_edge("negative_response",END)

work_flow = graph.compile()

review = "I have been using this app about a month and user interface and user experience is better but not like i want your payment system is good  but i have some issue with it and your customer support is not good."
result = work_flow.invoke({"review":review})
print(result)

