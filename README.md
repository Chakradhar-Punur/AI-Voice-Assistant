# AI-Voice-Assistant

This FastAPI-based AI Voice Assistant integrates with Dialogflow to provide interactive features such as:

Small Talk, Jokes, Weather Updates, Alarm Scheduling, FAQs

### Features:

* Uses Google Dialogflow for natural language understanding
* Supports multiple prebuilt agents (Small Talk, Jokes, Weather, Alarms)
* Uses MongoDB to store user queries
* Deployable as a Docker container
* Easy API-based interaction

###  Setup & Usage:

1)  Pull the Image from Docker Hub

`docker pull chakradharprime/voice-assistant:latest`

2) Run the Container

`docker run -p 8000:8000 \ -v /path/to/credentials:/app/credentials \ chakradharprime/voice-assistant:latest`

Note: Replace /path/to/credentials with the actual path to your Dialogflow credentials JSON files.

3) Access the API

(http://localhost:8000) : To view the home page
(http://localhost:8000/docs): To access the API

This will show the FastAPI Swagger UI with available API endpoints.

### API Endpoints:

### Send a User Query

POST /chat

Sends a query to Dialogflow and returns a response.

For example: 
{
  "user_input": "Tell me a joke"
}

### Folder Structure

/app
│-- main.py            # FastAPI application 
│-- credentials/       # Contains agent JSON credentials  
│-- Dockerfile         # Dockerfile for building the container  
│-- requirements.txt   # Python dependencies

### Docker Build & Push (For Developers)

If you make changes, rebuild the image:

`docker build -t chakradharprime/voice-assistant .`

Then, push it to Docker Hub:

`docker push chakradharprime/voice-assistant:latest`

### Notes

* Ensure that Google Cloud Dialogflow is configured correctly with valid credentials.
* Make sure your container is running before testing API endpoints.
