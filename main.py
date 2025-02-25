from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from google.cloud import dialogflow
from google.oauth2 import service_account
import datetime
import logging
import spacy
import uuid
import os

# initializing FastAPI
app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

class ChatRequest(BaseModel):
    user_input: str
    
nlp = spacy.load("en_core_web_sm")

DIALOGFLOW_AGENTS = {
    "jokes": {
        "project_id": "neon-water-367016",
        "credentials_path": "/app/credentials/Jokes-bot.json"
    },
    "small_talk": {
        "project_id": "reverberant-yew-376713",
        "credentials_path": "/app/credentials/Small-talk-bot.json"
    },
    "weather": {
        "project_id": "subtle-isotope-376716",
        "credentials_path": "/app/credentials/Weather-bot.json"
    },
    "FAQ": {
        "project_id": "western-grid-376705",
        "credentials_path": "/app/credentials/FAQ-bot.json"
    },
    "alarm": {
        "project_id": "my-new-project-451705",
        "credentials_path": "/app/credentials/Alarm-bot.json"
    }
}

SESSION_ID = str(uuid.uuid4())

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("⚠️ MONGODB_URI environment variable is not set!")

client = MongoClient(MONGODB_URI)
db = client["chatbot_db"]
collection = db["chat_logs"]

def save_chat(user_input, agent_key, intent, response):
    chat_entry = {
        "user_input": user_input,
        "agent": agent_key,
        "intent": intent,
        "response": response,
        "timestamp": datetime.datetime.now()
    }
    collection.insert_one(chat_entry)
    logging.info(f"Chat saved: {chat_entry}")
    
# recognizing user intent with pre defined keywords
# def recognize_intent(text: str):
#     keywords = {
#         "greeting": ["hello", "hi", "hey"],
#         "bye": ["bye", "goodbye", "see you"],
#         "weather": ["weather", "forecast", "temperature"]
#     }
#     for intent, words in keywords.items():
#         if any(word in text.lower() for word in words):
#             return intent
#     return "unknown"

def recognize_agent(user_text):
    doc = nlp(user_text.lower())
    
    if any(token.lemma_ in ["joke", "funny"] for token in doc):
        return "jokes"
    elif any(token.lemma_ in ["hello", "hi", "bye", "goodbye", "how", "you"] for token in doc):
        return "small_talk"
    elif any(token.lemma_ in ["weather", "forecast", "rain", "temperature"] for token in doc):
        return "weather"
    elif any(token.lemma_ in ["what", "do", "how", "where", "why", "compute", "engine"] for token in doc):
        return "FAQ"
    elif any(token.lemma_ in ["alarm", "wake", "repeat", "day", "check", "show", "set"] for token in doc):
        return "alarm"
    
    return None

def get_response_dialogflow(text, agent_key):
    if agent_key not in DIALOGFLOW_AGENTS:
        return "unknown", "I'm not sure how to respond to that."

    agent = DIALOGFLOW_AGENTS[agent_key]

    credentials = service_account.Credentials.from_service_account_file(agent["credentials_path"])
    session_client = dialogflow.SessionsClient(credentials=credentials)

    session = session_client.session_path(agent["project_id"], SESSION_ID)
    text_input = dialogflow.TextInput(text=text, language_code="en")
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result.intent.display_name, response.query_result.fulfillment_text

@app.get("/")
async def home():
    return {"message": "Welcome to the AI Voice Assistant API!"}

# Creating the /chat API Endpoint
@app.post("/chat/")
async def chat(request: ChatRequest):
    user_text = request.user_input
    logging.info(f"User Input: {user_text}")
    
    agent_key = recognize_agent(user_text)
    
    # this segment of code is for keyword matching.
    # response = recognize_intent(user_text)
    # response = {
    #     "greeting": "Hello! How can I assist you?",
    #     "bye": "Goodbye! Have a nice day.",
    #     "weather": "I can check the weather for you. Could you tell me your location",
    #     "unknown": "I didn't quite get that! Could you please repeat it?"
    # }.get(intent, "I didn't understand that.")
    # logging.info(f"Response: {response}")
    
    # To improve the voice assistant, I have used Dialogflow to handle both simple and complex queries
    if agent_key:
        intent, response = get_response_dialogflow(user_text, agent_key)
    else:
        intent, response = "unknown", "I'm not sure how to respond to that."
 
    logging.info(f"Agent: {agent_key}, Intent: {intent}, Response: {response}")
    
    save_chat(user_text, agent_key, intent, response)

    return {"agent": agent_key, "intent": intent, "response": response}
