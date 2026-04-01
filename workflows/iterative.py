from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage
from dotenv import load_dotenv
from pydantic import BaseModel, Field 
from typing import TypedDict,Annotated,Literal
import operator
import json
load_dotenv(

)

generator_llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
optimizer_llm = ChatOpenAI(model="gpt-4o-mini")


class XState(TypedDict):
    topic:str
    tweet:str
    evaluation:Literal["approved","need improvement"]
    feedback:str
    iteration:int
    max_iterations:int

def generate_tweet(state:XState)->XState:
    message = [
        SystemMessage(content="You are funny tweeter/X influencer your name is X."),
        HumanMessage(content=f"generate a short,  original and funny tweet on the topic:{state["topic"]}: rules: do not use q and a format max 200 characters  "),
    ]
    response = generator_llm.invoke(message).content
    return {"tweet":response}

class TweetEvaluationSchema(BaseModel):
    evaluation:Literal["approved","need improvement"] = Field(...,description="The evaluation result for the tweet")
    feedback:str = Field(...,description="Feedback on how to improve the tweet if it needs improvement")

structured_evaluator = evaluator_llm.with_structured_output(TweetEvaluationSchema)

def evaluate_tweet(state:XState)->XState:
    messages = [SystemMessage(content="You are a strict and critical evaluator for tweets. You evaluate the tweet based on its originality, humor, and relevance to the topic. You give feedback on how to improve the tweet if it does not meet the standards."),
                HumanMessage(content=f"Evaluate the following tweet: {state['tweet']} on the topic: {state['topic']}. Provide feedback and determine if the tweet is approved or needs improvement.")]
    result = structured_evaluator.invoke(messages)
    return {"evaluation": result.evaluation, "feedback": result.feedback}

def optimize_tweet(state:XState)->XState:
    messages = [
        SystemMessage(content="you punchup tweet for virality and humor based on given feedback"),
        HumanMessage(content=f"Improve the tweet based on the feedback:{state["feedback"]} Topic:{state["topic"]} originalTweet:{state["tweet"]} rewrite is at short , humor zero vulgur and stay with 200 max characters"),

    ]
    r = optimizer_llm.invoke(messages["messages"][-1].content)
    iteration = state["iteration"]+1
    return{"tweet":r,"iteration":iteration}



def route_eval(state:XState)->XState:
    if state["evaluation"] == "approved" or state["iteration"] >= state["max_iterations"]:
        return "approved"
    else:
        return "need_improvement"


graph = StateGraph(XState)
graph.add_node("generate_tweet",generate_tweet)
graph.add_node("evaluate_tweet",evaluate_tweet)
graph.add_node("optimize_tweet",optimize_tweet)

graph.add_edge(START,"generate_tweet")
graph.add_edge("generate_tweet","evaluate_tweet")
graph.add_conditional_edges("evaluate_tweet",route_eval,{"approved":END,"need_improvement":"optimize_tweet"})
graph.add_edge("optimize_tweet","evaluate_tweet")

workflow = graph.compile()
init_state = {
    "topic":"One Piece",
    "iteration":1,
    "max_iterations":5
}

result = workflow.invoke(init_state)
print(result)



