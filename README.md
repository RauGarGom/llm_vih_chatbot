# vihsible - a virtual hug

**vihsible** is a chatbot developed as a final team project for the [Spanish LGTBI+ Federation (FELGTBI+)](https://felgtbi.org/). This tool uses state-of-the-art technologies such as **LangChain**, **Cohere LLM**, **FastAPI**, and **PostgreSQL** to provide meaningful and context-aware responses to user inquiries.  

## Project Overview  

**vihsible** leverages multiple autonomous LLM agents that collaborate to identify the type of question posed by the user. Based on the user's input, the chatbot dynamically selects and executes the appropriate prompt to deliver relevant and accurate answers. Additionally, the chatbot asks a series of follow-up questions planned by an administrator. These follow-ups are filtered by the AI according to the prior knowledge it has about the user, creating a personalized and efficient interaction experience.  

### Key Features  
- **Autonomous Prompt Coordination**: Different prompts interact and exchange information to respond accurately to user queries.
- **Personalized User Interaction**: Follow-up questions are tailored based on the chatbot's understanding of the user.  
- **Backend and Database Hosting**: The backend is deployed on AWS EC2, and the database is hosted on AWS RDS for scalability and reliability.  
- **FastAPI and PostgreSQL Integration**: A robust and efficient backend architecture.  

### Technologies Used  
- **LangChain**: To manage and structure LLM interactions.  
- **Cohere LLM**: As the primary language model for generating responses.  
- **FastAPI**: For building a high-performance RESTful API.  
- **PostgreSQL**: For handling persistent data storage.  
- **AWS EC2 & RDS**: For hosting the backend and database infrastructure.  

## Development Team  
The AI backend part of the project, shown is this repository, was made by:
- [Alejandro Villarreal](https://github.com/alexvillaro2003)
- [Raúl García](https://github.com/RauGarGom)
- [Sengan Nije](https://github.com/sengan9)
- [Tamara Acedo](https://github.com/alexvillaro2003)

## Getting Started  

### Prerequisites  
- PostgreSQL with credentials
- A Cohere API key

### Installation
1. A dockerized, ready-to-use image can be used with the following code:
  ```
  docker pull raugargom/desafio_backend_test:v3
  ```
Check the [DockerHub page](https://hub.docker.com/repository/docker/raugargom/desafio_backend_test/general) to make sure you're using the latest version.

2. The user needs to create a .env, in the same folder of the image. It should have a similar structure as the following example:
```
COHERE_TRIAL_API_KEY=...
POSTGRE_PASS=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
```
3. Run the image with a code like this:
```
docker run --env-file .env -p 8000:8000 -t raugargom/desafio_backend_test:v3.1
```


    

