from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRALAI_API_KEY"))

chat_response = client.chat.complete(
    model=os.getenv("MISTRALAI_MODEL"),
    messages=[{"role":"user", "content":"Left 4 dead é a mesma coisa que back 4 blood?"}]
)

print(chat_response.choices[0].message.content)