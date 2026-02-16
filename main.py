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
from pydantic import BaseModel, Field
import pandas as pd
install tabulate

# 1. API Keys from Secrets
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# 2. Setup the Model
gpt4o = ChatOpenAI(model_name="gpt-4o")

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

st.text ("Sample Prompt: Give the changelogs for campaign 478986, starting from January 1, 2026, until February 08, 2026.")

# --- Model Initialization ---
# Initialize Google's Gemini 1.5 Flash model via LangChain's
# ChatGoogleGenerativeAI wrapper. Flash is optimized for speed and efficiency.

# --- LangChain Pipeline ---
# Chain the prompt template and model together using LangChain's pipe operator.
# When invoked, the prompt is formatted first, then passed to the model.
#tweet_chain = tweet_prompt | gpt4o


user_input = st.text_input("User Prompt")

extraction_prompt = """Your task is to extract the campaign ID, start date, and end date from the user's natural language input.
The campaign ID should be an integer.
The start date and end date should be in 'YYYY-MM-DD' format.
Your output must be a JSON object.
Here is the user's input: {user_input}
"""
print("Extraction prompt defined.")

class CampaignDetails(BaseModel):
    campaign_id: int = Field(description="The ID of the campaign, as an integer")
    start_date: str = Field(description="The start date in 'YYYY-MM-DD' format")
    end_date: str = Field(description="The end date in 'YYYY-MM-DD' format")

    

if st.button("Fetch"):    

    formatted_prompt = extraction_prompt.format(user_input=user_input)
    
    #print("Sending request to LLM with structured output...")
    
    # Create a structured LLM by binding the Pydantic model
    structured_llm = gpt4o.with_structured_output(CampaignDetails, method="json_mode")
    
    # Invoke the structured LLM
    parsed_data = structured_llm.invoke(formatted_prompt)
    
    print("LLM response received and parsed.")
    
    # Store the extracted values in separate variables
    campaign_id = parsed_data.campaign_id
    start_date = parsed_data.start_date
    end_date = parsed_data.end_date
    
    print(f"Extracted Campaign ID: {campaign_id}")
    print(f"Extracted Start Date: {start_date}")
    print(f"Extracted End Date: {end_date}")


    # Generate button - invokes the LangChain pipeline and displays the results
    
    base_url = "https://console.kayzen.io/api/v1/rtbx/campaigns/{campaign_id}/changelogs"
    
    # Assuming campaign_id, start_date, and end_date are available from previous LLM extraction
    # If they are not yet executed, they will default to initial values. 
    # It's recommended to run the LLM extraction cell (5d3972f0) first to get the latest values.
    
    # Construct the URL with query parameters
    url = f"{base_url.format(campaign_id=campaign_id)}?end_time={end_date}&start_time={start_date}"
    
    # Use the global access_token_global variable
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token_global}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        print("Status Code:", response.status_code)
        response_data = response.json()
        
        # Prepare data for table
        table_data = []
        for log in response_data.get('data', []):
            log_id = log.get('id')
            campaign_id = log.get('loggable_id')
            action = log.get('action')
            username = log.get('username')
            updated_at = log.get('loggable_updated_at')
            
            # Summarize data_diff
            data_diff = log.get('data_diff', {})
            changes_summary = []
            for key, value in data_diff.items():
                if key == 'creatives' and value:
                    # Check if 'old' and 'new' exist and are different
                    old_creatives_status = {c.get('id'): c.get('status') for c in value.get('old', [])}
                    new_creatives_status = {c.get('id'): c.get('status') for c in value.get('new', [])}
                    if old_creatives_status != new_creatives_status:
                        changes_summary.append('Creatives status updated')
                    elif value.get('old') or value.get('new'): # if there are creatives, just say updated
                        changes_summary.append('Creatives updated')
                elif key == 'trackers' and value:
                    if value.get('old') or value.get('new'):
                        changes_summary.append('Trackers updated')
                elif key == 'bid_values' and value:
                    if value.get('old') or value.get('new'):
                        changes_summary.append('Bid values updated')
                elif key == 'targeting' and value:
                    if value.get('old') or value.get('new'):
                        changes_summary.append('Targeting updated')
                elif value: # For other changes, just note the field name
                    changes_summary.append(f"{key.replace('_', ' ').title()} updated")
    
            if not changes_summary:
                changes_summary.append('No significant data changes recorded')
                
            table_data.append({
                'ID': log_id,
                'Campaign ID': campaign_id,
                'Action': action,
                'User': username,
                'Updated At (UTC)': updated_at,
                'Changes': ', '.join(changes_summary)
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            print("\n--- Changelogs Table ---\n")
            st.write(df.to_markdown(index=False))
        else:
            print("No changelog data found.")
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print("Response Body (error):", response.text)
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
        
        #st.write(response) # Note: Added .json() to make it readable


    
