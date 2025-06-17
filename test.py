import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env and get the API key
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=google_api_key)

# Load your image
with open("/home/ehwkang/DTS_folked/image/Brooks_1.png", "rb") as image_file:
    image_bytes = image_file.read()

# Create the model instance
model = genai.GenerativeModel("gemini-2.5-pro")

# Send the image as input
response = model.generate_content([
    "Describe this image.",
    {
        "mime_type": "image/jpeg",
        "data": image_bytes
    }
])

print(response.text)
