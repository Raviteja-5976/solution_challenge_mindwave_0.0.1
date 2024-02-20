# for sending email
import smtplib
# for speech recognition 
import speech_recognition as sr
# for text to speech conversi0on
import pyttsx3
# for email message format
from email.message import EmailMessage
# for date & time
import datetime

import requests
# to open images 
from PIL import Image
# to read byte code
from io import BytesIO
import random
# to access webbrowser
import webbrowser  
# google genai package
import google.generativeai as genai 
#openai package
from openai import OpenAI
# for camera usage
import cv2

import os
# To control mouse
import pyautogui
# To control keyboard
import keyboard

import pywhatkit

# Initialise recogniser
listener = sr.Recognizer()
# initialise Text to speech engine
engine = pyttsx3.init()

# Configure Google Gemini API key
genai.configure(api_key="GEMINI_API_KEY")

# Weather API key
wh_api_key = "OPEN_WEATHER_API_KEY"
# Openai API key
openai_api_key = 'OPENAI_API_KEY'

client = OpenAI(api_key= openai_api_key)

# Load environment variables for API keys and other sensitive information
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Setting up Gemini Model 
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]


# function for text to speech operation
def talk(text):
    print(text)
    engine.say(text)
    engine.runAndWait()


# Speech recognition function
def get_info():
    try:
        with sr.Microphone() as source:
            print('listening...')
            voice = listener.listen(source)
            info = listener.recognize_google(voice)
            print(info)
            return info.lower()
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")



# For handling intent         
def intent_recognition(user_input):
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    prompt = f'''You are a one-word answer bot. Your responses should be in the format ["key_word", "query"].
        You can only use one of the following words for key_word: 'question,' 'weather,' 'email,' 'camera,' 'time,' 'youtube,' 'chat,' 'image_creation,' 'whatsapp_message,' 'vision,' 'analyse,' 'web,' 'greetings,' 'goodbye,' 'gratitude,' 'apologies,' 'positive_feedback,' or 'negative_feedback.'
        Now, please provide your statement in the following format: ["key_word", "user_query"].". Note : The 'vision' keyword is used when the user asks to analyse what's on screen. 
        Do not forget the format you have to reply ["key_word", "query"]. This is in dictionary form in python. If the user didn't specify the user_query then don't give the user_query, just give me the keyword. 
        Now the user input is "{user_input}" '''

    response = model.generate_content(prompt)
    res = response.text.strip("[]")
    response_parts = res.split(", ", 1)  # Splitting only on the first comma to ensure two parts are generated.

    if len(response_parts) >= 2:
        intent = response_parts[0].strip('"')
        query = response_parts[1].strip('"')
        handle_intent(intent=intent, query=query)
    else:
        # Handle the error case where the response does not contain enough parts
        talk("I'm sorry, I didn't understand that. Could you please rephrase your request?")
        # Optionally, log the response for debugging
        print(f"Unexpected response format: '{response.text}'")


# for weather
def weather(api_key, city = None):
    if not city:
        talk("Please tell me the name of the city.")
        city = get_info()

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200:
            main_weather = data['weather'][0]['main']
            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']

            weather_report = f"The weather in {city} is {main_weather}, {description}. "
            weather_report += f"The temperature is {temperature} degrees Celsius, and humidity is {humidity}%."

            talk(weather_report)
        else:
            error_message = f"Error: {data['message']}"
            talk(error_message)

    except requests.RequestException as e:
        error_message = f"Error: {e}"
        talk(error_message)

#for youtube search
def youtube(query):
    youtube_url = "https://www.youtube.com/results?search_query="
    search_query = query.replace(' ', '+')
    search_url = f"{youtube_url}{search_query}"

    webbrowser.open(search_url)
    talk('Hey! I have searched the youtube video, do you need anything more')
    des = get_info()
    if des == "no":
        exit()

# To get email info
def get_email_info():
    try:
        talk('Please tell me the email address of the recipient.')
        email_address = input()  # Use get_info to get the email address
        talk('What is the subject of your email?')
        subject = get_info()
        talk('Tell me the text in your email')
        text = get_info()
        message = text_message_email(text)
        send_email(email_address, subject, message)
        talk('Hey. Your email is sent.')
        talk('Do you want to send more email?')
        send_more = get_info()
        if 'yes' in send_more:
            get_email_info()
        elif 'no' in send_more:
            main()
    except Exception as e:
        talk(f"An error occurred: {e}")


# To send email
def send_email(email_address, subject, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Replace with your email and password
        sender_email = 'raviteja.gdsc@gmail.com'
        sender_password = 'ufxd ytiw ampu ymtx'
        server.login(sender_email, sender_password)
        email = EmailMessage()
        email['From'] = sender_email
        email['To'] = email_address
        email['Subject'] = subject
        email.set_content(message)
        server.send_message(email)
        server.quit()
        talk("Email sent successfully.")
    except Exception as e:
        talk(f"An error occurred: {e}")





        
# To generate email content
def text_message_email(email_info):
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    talk('Please tell me the name of receipient')
    to_name = get_info()
    send_name = "Raviteja"
    prompt = f'You are a email writing bot. Write an email to {to_name} about "{email_info}". The email is from {send_name}. Write only the email, do not wirte anything except that.'
    response = model.generate_content(prompt)
    print(response.text)
    return response.text


# To generate Photo
def gen_photo(prompt):
    if prompt is None:
        talk('Sir, Please tell me what I have to create')
        prompt = input() # Use get_info() to get the user input

    response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url
    # gen_url = response["data"][0]["url"]
    rep = requests.get(image_url)
    img_data = BytesIO(rep.content)

    img = Image.open(img_data)
    img.show()
    talk('Here is the generated photo for the provided prompt.')

# For Vision
def vision():
    pass

# To access camera
def camera():
    # Open the default camera (usually the built-in webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    # Create a folder to save the captured photos (if it doesn't exist)
    save_folder = "captured_photos"
    os.makedirs(save_folder, exist_ok=True)

    photo_count = 0

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to read a frame.")
            break

        # Display the frame in a window
        cv2.imshow("Camera Feed", frame)

        # Save the frame as an image in the 'captured_photos' folder
        photo_filename = os.path.join(save_folder, f"photo_{photo_count}.jpg")
        cv2.imwrite(photo_filename, frame)

        # Increment the photo count
        photo_count += 1

        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()  


# to ask question
def ask_now(query):
    model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)


    prompt_parts = query

    response = model.generate_content(prompt_parts)
    talk(response.text)
    return


# To chat with bot
def chat():
    pass

# For web browsing
def web(query):
    search_url = f'https://www.google.com/search?q={query}'
    webbrowser.open(search_url)

def whatsapp():
    talk("Please tell me the numnber of the receipient")
    receive = input()
    talk('Please tell me what is the message')
    msg = get_info()
    talk('please wait to send the message')
    send = pywhatkit.sendwhatmsg(receive, msg)
    if send == True:
        talk('Your message is been sent, Do you want more messages to send?')
        repeat = get_info()
        if repeat == 'no':
            main()
        else:
            whatsapp()


def handle_intent(intent, query):
    # ... (Your handle_intent function here)
    if intent == "greetings":
        genral_intent(genral="greetings")

    elif intent == "goodbye":
        genral_intent(genral="goodbye")
        exit()

    elif intent == "apologies":
        genral_intent(genral="apologies")

    elif intent == "positive_feedback":
        genral_intent(genral="positive feedback")

    elif intent == "negative_feedback":
        genral_intent(genral="negative feedback")

    elif intent == "weather":
        weather(api_key = wh_api_key, city= query)

    elif intent == "email":
        get_email_info()

    elif intent == "image_creation":
        gen_photo(prompt= query)

    elif intent == "whatsapp_message":
        whatsapp()

    elif intent == "youtube":
        if query is None:
            talk("Please tell me what video you want to see")
            question = get_info()
            youtube(query= question)
        else:
            youtube(query = query)

    elif intent == "time":
        date = datetime.datetime.now()
        talk(f'Today date and time is {date}')

    elif intent == "vision":
        vision()

    elif intent == "question":
        ask_now(query)

    elif intent == "chat":
        chat()

    elif intent == "webbrowsing":
        web(query=query)



# Function for general intent
def genral_intent(genral):
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    
    prompt = f"You are a voice assistant and this is the total intent of the user {genral}. Now based on this intent give me an appropriate response for the user. Only give me one response as if you now giving the response to user as an assistant now. Give me the response below ten words."
    response = model. generate_content(prompt)
    return talk(response.text)
    
        

# Taking the input and giving the intent to intent_recognition 
def main():
    # to take input infinite times.
    # start_listening()
    talk("Hi! I am your personal assistant. How can I help you today")
    while True:
        user_input = get_info()

        intent_recognition(user_input=user_input)



if __name__ == "__main__":
    main()
