import aiml
import wikipediaapi
import cgi
from langdetect import detect
from googletrans import Translator
import os
import sys
import contextlib


STATUS_FILE = "E:/Final Year Project/TeckTrendz/server/Chatbot/chat_state.txt"

USER_AGENT = 'MyChatbot/1.0 (mychatbot@example.com)'
wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=USER_AGENT)
translator = Translator()

def setup_aiml():
    kernel = aiml.Kernel()
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            kernel.bootstrap(learnFiles="startup.xml", commands="load aiml b")
    return kernel

def get_wikipedia_summary(topic):
    topic = topic.replace('_', ' ')
    page = wiki_wiki.page(topic)
    if page.exists():
        return page.summary
    return "I couldn't find any information on that topic."

def translate_text(text, dest_language):
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except:
        return text

def get_response_language(user_input):
    try:
        stripped = user_input.strip().lower()
        known_greetings = {
            "hola": "es", "bonjour": "fr", "hallo": "de", "ciao": "it",
            "hej": "sv", "merhaba": "tr", "salut": "fr", "مرحبا": "ar",
            "こんにちは": "ja", "你好": "zh-cn",
        }
        if stripped in known_greetings:
            return known_greetings[stripped]
        if len(stripped) < 5:
            return 'en'
        return detect(user_input)
    except:
        return 'en'

def translate_response_if_needed(response, user_input):
    input_lang = get_response_language(user_input)
    if input_lang != 'en':
        return translate_text(response, input_lang)
    return response

def process_commands(answer, translated_input):
    params = answer[1:].split('$')
    cmd = int(params[0])
    if cmd == 0:
        return translate_text(params[1], detect(translated_input))
    elif cmd == 1:
        topic = params[1]
        summary = get_wikipedia_summary(topic)
        return translate_text(summary, detect(translated_input))
    elif cmd == 98:
        return "Please provide your Order ID."
    elif cmd == 99:
        return translate_text("I didn't get that, please try again.", detect(translated_input))
    else:
        return "Unknown command."

if __name__ == "__main__":
    user_input = sys.stdin.readline().strip()
    kernel = setup_aiml()

    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            waiting = f.read().strip() == "waiting_for_order_id"
    else:
        waiting = False

    if waiting:
        try:
            with open("E:/Final Year Project/TeckTrendz/server/orders.txt", "r") as f:
                orders = f.readlines()
            match = next((line for line in orders if f"Order ID: {user_input}" in line), None)
            response = match.strip() if match else "Sorry, I couldn't find that order ID."
        except:
            response = "Error reading order file."
        os.remove(STATUS_FILE)
    else:
        user_lang = get_response_language(user_input)
        translated_input = translate_text(user_input, 'en')
        answer = kernel.respond(translated_input)

        if answer.startswith('#'):
            if "#98$" in answer:
                with open(STATUS_FILE, "w") as f:
                    f.write("waiting_for_order_id")
            response = process_commands(answer, translated_input)
        else:
            response = answer if user_lang == 'en' else translate_text(answer, user_lang)

    # ✅ FINAL OUTPUT ONLY
    print(response)
