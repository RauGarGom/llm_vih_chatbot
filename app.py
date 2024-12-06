from fastapi import FastAPI

import uvicorn

app = FastAPI()

# Mount the static files directory

# Initialize Jinja2 templates

# Global variable so evaluate gets the same question as generate


app = FastAPI()
@app.get('/')
async def home():
    return "Test API. Si ves esto, funciona!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
