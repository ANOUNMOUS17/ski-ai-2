from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
from googletrans import Translator
import webbrowser
import os
import random
import sympy as sp
from datetime import datetime
import threading

app = Flask(__name__)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize the translator
translator = Translator()

# Log file to write all spoken responses
log_file = "spoken_responses.txt"

def speak(text):
    def run_speech():
        prefixed_text = f"Marcus I says: {text}"
        # Write the response to the log file
        with open(log_file, "a") as file:
            file.write(prefixed_text + "\n")
        # Speak the response
        engine.say(prefixed_text)
        engine.runAndWait()
    
    # Run the speech in a separate thread
    threading.Thread(target=run_speech).start()

def greet_user():
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good afternoon!"
    elif 18 <= current_hour < 21:
        greeting = "Good evening!"
    else:
        greeting = "Good night!"
    return greeting

def get_time_info(info_type):
    now = datetime.now()
    if info_type == 'time':
        return now.strftime("%H:%M:%S")
    elif info_type == 'day':
        return now.strftime("%A")
    elif info_type == 'date':
        return now.strftime("%d %B %Y")
    elif info_type == 'year':
        return now.strftime("%Y")
    return "PLEASE TRY AGAIN I AM READY FOR IT."

def translate_text(text, dest_language):
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        return f"Error: {str(e)}"

def handle_translation(command):
    if 'translate' in command:
        parts = command.split('into')
        if len(parts) == 2:
            text = parts[0].replace("translate", "").strip()
            dest_language = parts[1].strip().lower()
            translation = translate_text(text, dest_language)
            return f"The translation is: {translation}"
        else:
            return "Please specify the text and target language."
    return "No translation command found."

def handle_command(command):
    if 'open youtube' in command:
        webbrowser.open("https://www.youtube.com")
    elif 'open chrome' in command:
        os.system("start chrome")
    elif 'exit' in command:
        speak("Exiting...")
        return True
    return False

def handle_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the math book look sad? Because it had too many problems.",
        "Why don't programmers like nature? It has too many bugs."
    ]
    return random.choice(jokes)

def handle_math(command):
    try:
        expression = command.replace("solve", "").strip()
        result = sp.sympify(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def handle_summarization(command):
    # Simplified summarization by truncating long text
    text_to_summarize = command.replace("summarize", "").strip()
    if len(text_to_summarize) > 50:
        return text_to_summarize[:50] + "..."
    else:
        return text_to_summarize

@app.route('/')
def index():
    try:
        greeting = greet_user()
        speak(greeting)
        return render_template('index.html', greeting=greeting)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/my_ai_company')
def my_ai_company():
    return render_template('my_ai_company.html')

@app.route('/command', methods=['POST'])
def command():
    command = request.json.get('command')
    response = "I didn't understand that command."
    
    if handle_command(command):
        response = "Exiting..."
    elif 'translate' in command:
        response = handle_translation(command)
    elif 'joke' in command:
        response = handle_joke()
    elif 'solve' in command:
        response = handle_math(command)
    elif 'summarize' in command:
        response = handle_summarization(command)
    elif 'time' in command:
        response = f"The current time is {get_time_info('time')}."
    elif 'day' in command:
        response = f"Today is {get_time_info('day')}."
    elif 'date' in command:
        response = f"Today's date is {get_time_info('date')}."
    elif 'year' in command:
        response = f"The current year is {get_time_info('year')}."
    
    speak(response)
    return jsonify(response=response)

if __name__ == "__main__":
    app.run(debug=True)
