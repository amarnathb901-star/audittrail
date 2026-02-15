# ============================================================
# Tweet Generator - Main Application
# A Streamlit app that generates tweets using Google's Gemini
# AI model, orchestrated through LangChain.
# ============================================================

# --- Imports ---
# LangChain components for LLM interaction and prompt management
import streamlit as st
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# --- API Key Configuration ---
# Load the Google API key from Streamlit's secrets manager
# and set it as an environment variable for the Google GenAI client.
# The key should be defined in .streamlit/secrets.toml
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Import ChatOpenAI module
from langchain_openai import ChatOpenAI

# Initialize OpenAI's GPT-4o-mini
#gpt4o_mini = ChatOpenAI(model_name = "gpt-4o-mini")  # use "gpt-4o" for larger GPT-4 model

gpt4o = ChatOpenAI(model_name = "gpt-4o")

# Using Google Models (Gemini Flash)
#from langchain_google_genai import ChatGoogleGenerativeAI

# --- Prompt Template ---
# Define the prompt template with placeholders for the number of tweets
# and the topic. LangChain's PromptTemplate handles variable substitution.
tweet_template = "Give me {number} tweets on {topic}"

tweet_prompt = PromptTemplate(template = tweet_template, input_variables = ['number', 'topic'])

# --- Model Initialization ---
# Initialize Google's Gemini 1.5 Flash model via LangChain's
# ChatGoogleGenerativeAI wrapper. Flash is optimized for speed and efficiency.

# --- LangChain Pipeline ---
# Chain the prompt template and model together using LangChain's pipe operator.
# When invoked, the prompt is formatted first, then passed to the model.
tweet_chain = tweet_prompt | gpt4o

# --- Streamlit UI ---
# Page header and description
import streamlit as st

st.header("🐦 Tweet Generator")

st.subheader("Generate tweets using Generative AI 🤖")

# Text input for the user to specify a tweet topic
topic = st.text_input("Topic")

# Numeric input to select how many tweets to generate (between 1 and 10)
number = st.number_input("Number of tweets", min_value = 1, max_value = 10, value = 1, step = 1)

# Generate button - invokes the LangChain pipeline and displays the results
if st.button("Generate"):
    tweets = tweet_chain.invoke({"number" : number, "topic" : topic})
    st.write(tweets.content)
    
