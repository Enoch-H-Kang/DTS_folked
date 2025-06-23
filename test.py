import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests

# Load .env and get the API key
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=google_api_key)

# Directory to save images
output_dir = "image/generated_ads"
os.makedirs(output_dir, exist_ok=True)


# Load your image
with open("/home/ehwkang/DTS_folked/image/Brooks_1.png", "rb") as image_file:
    image_bytes = image_file.read()

# Create the model instance
model = genai.GenerativeModel("gemini-2.5-pro")

# Send the image as input
response = model.generate_content([
    "Describe this image.",
    {
        "mime_type": "image/png",
        "data": image_bytes
    }
])

print(response.text)
