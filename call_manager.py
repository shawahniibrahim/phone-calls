import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class CallManager:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.server_url = os.getenv("SERVER_URL")
        
        if not all([self.account_sid, self.auth_token, self.from_number, self.server_url]):
            raise ValueError("Missing Twilio credentials or SERVER_URL in .env")

        self.client = Client(self.account_sid, self.auth_token)

    def make_call(self, to_number: str):
        """
        Initiates a call to the specified number.
        The 'url' parameter points to our FastAPI /voice endpoint.
        """
        call = self.client.calls.create(
            to=to_number,
            from_=self.from_number,
            url=f"{self.server_url}/voice"
        )
        return call.sid

if __name__ == "__main__":
    # Test usage
    try:
        manager = CallManager()
        # manager.make_call("+1234567890") 
        print("CallManager initialized successfully.")
    except Exception as e:
        print(f"Error initializing CallManager: {e}")
