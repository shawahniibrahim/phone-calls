import os
import uvicorn
from pyngrok import ngrok
from dotenv import load_dotenv

def main():
    # Load environment variables (for OpenAI/Twilio keys)
    load_dotenv()

    # Check for ngrok auth token
    auth_token = os.getenv("NGROK_AUTHTOKEN")
    if auth_token:
        ngrok.set_auth_token(auth_token)
    else:
        print("Warning: NGROK_AUTHTOKEN not set in .env. Ngrok session might expire or fail.")
    
    # Start ngrok tunnel
    port = 8000
    public_url = ngrok.connect(port).public_url
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

    # Update the environment variable so the app knows its own URL
    os.environ["SERVER_URL"] = public_url

    # Start the FastAPI server
    # We use the string import "server:app" so uvicorn can reload if needed, 
    # but programmatically we might need to pass the app object if we want to share the env var easily 
    # across processes if reload is on. 
    # However, with reload=False, os.environ is shared. 
    # If reload=True, uvicorn spawns a subprocess which might not inherit the *updated* env var 
    # unless we are careful.
    # For simplicity, we will run without reload for this auto-script, or user can manually set it.
    
    print(" * Starting server...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
