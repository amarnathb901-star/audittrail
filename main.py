# ============================================================
# Tweet Generator - Main Application
# A Streamlit app that generates tweets using Google's Gemini
# AI model, orchestrated through LangChain.
# ============================================================

# --- Imports ---
# LangChain components for LLM interaction and prompt management
# --- Imports ---
import streamlit as st
import os
import requests
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 1. API Keys from Secrets
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# 2. Setup the Model
gpt4o = ChatOpenAI(model_name="gpt-4o")

# 3. Define a helper function to get the token (so it doesn't crash)
def get_kayzen_token():
    url = "https://api.kayzen.io/v1/authentication/token"
    # Move these credentials to st.secrets['KAYZEN_BASIC_AUTH']
    headers = {
        "accept": "application/json",
        "authorization": st.secrets['KAYZEN_BASIC_AUTH'],
        "content-type": "application/json"
    }
    payload = {
        "grant_type": "password",
        "username": "amarnath.bs+liga_advaccmgr@kayzen.io",
        "password": ['PWD']
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get('access_token')

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


url = "https://api.kayzen.io/v1/authentication/token"

headers = {
    "accept": "application/json",
    "authorization": st.secrets['KAYZEN_BASIC_AUTH'],
    "content-type": "application/json"
}

payload = {
    "grant_type": "password",
    "username": "amarnath.bs+liga_advaccmgr@kayzen.io",
    "password": st.secrets['PWD']
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    print("Status Code:", response.status_code)
    response_data = response.json()
    print("Response Body:", response_data)
    global access_token_global
    access_token_global = response_data.get('access_token')
    print(f"Access Token stored: {access_token_global}")
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    print("Response Body (error):", response.text)
except requests.exceptions.ConnectionError as conn_err:
    print(f"Connection error occurred: {conn_err}")
except requests.exceptions.Timeout as timeout_err:
    print(f"Timeout error occurred: {timeout_err}")
except requests.exceptions.RequestException as req_err:
    print(f"An unexpected error occurred: {req_err}")


import streamlit as st

st.header("Changelogs")

st.subheader("Enter the campaign id and the date range")

# Generate button - invokes the LangChain pipeline and displays the results
if st.button("Fetch"):    
    campaign_id = st.number_input("Campaign Id")
    
    date_range = st.date_input("Date Range")
    
    base_url = "https://api.kayzen.io/v1/campaigns/{campaign_id}/changelogs"
    
    url = base_url.format(campaign_id=campaign_id)
    
    # Use the global access_token_global variable
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token_global}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        print("Status Code:", response.status_code)
        print("Response Body:", response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print("Response Body (error):", response.text)
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
    
    st.write(response.json()) # Note: Added .json() to make it readable


# --- Prompt Template ---
# Define the prompt template with placeholders for the number of tweets
# and the topic. LangChain's PromptTemplate handles variable substitution.
tweet_template = "Give me the changelog for campaign {campaign_id} for the date range {date_range}"

tweet_prompt = PromptTemplate(template = tweet_template, input_variables = ['campaign_id', 'date_range'])

# --- Model Initialization ---
# Initialize Google's Gemini 1.5 Flash model via LangChain's
# ChatGoogleGenerativeAI wrapper. Flash is optimized for speed and efficiency.

# --- LangChain Pipeline ---
# Chain the prompt template and model together using LangChain's pipe operator.
# When invoked, the prompt is formatted first, then passed to the model.
tweet_chain = tweet_prompt | gpt4o

# --- Streamlit UI ---
# Page header and description



    
