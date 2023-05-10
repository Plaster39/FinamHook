import uvicorn
from Hook.webhook_handler import app
from config import IP_SERVER
if __name__ == "__main__":
    uvicorn.run(app, host=IP_SERVER, port=8000)
