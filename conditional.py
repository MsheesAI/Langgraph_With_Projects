from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import TypedDict,Annotated
import operator

load_dotenv(

)

model = ChatOpenAI(model="gpt-4o-mini")