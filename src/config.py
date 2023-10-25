from dotenv import load_dotenv
import os

load_dotenv()

discord_token = os.getenv("TOKEN")
author_id = os.getenv("AUTHOR_ID")