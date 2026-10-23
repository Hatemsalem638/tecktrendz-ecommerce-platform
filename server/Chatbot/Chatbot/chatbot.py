import aiml
import wikipediaapi
import cgi
from langdetect import detect
from googletrans import Translator

USER_AGENT = 'MyChatbot/1.0 (mychatbot@example.com)'
wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=USER_AGENT)
translator = Translator()

def setup_aiml():
    kernel = aiml.Kernel()
    if not kernel.bootstrap(learnFiles="startup.xml", commands="load aiml b"):
        kernel.saveBrain("bot_brain.brn")
    else:
        kernel.loadBrain("bot_brain.brn")
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
    except Exception as e:
        print(f"Failed to translate due to: {str(e)}")
        return text

def get_response_language(user_input):
    try:
        stripped = user_input.strip().lower()
        known_greetings = {
            "hola": "es",
            "bonjour": "fr",
            "hallo": "de",
            "ciao": "it",
            "hej": "sv",
            "merhaba": "tr",
            "salut": "fr",
            "مرحبا": "ar",
            "こんにちは": "ja",
            "你好": "zh-cn",
        }

        if stripped in known_greetings:
            return known_greetings[stripped]
        if len(stripped) < 5:
            return 'en'

        return detect(user_input)
    except:
        return 'en'



def respond_in_user_language(response, user_input):
    input_lang = get_response_language(user_input)
    if input_lang != 'en':
        return translate_text(response, dest_language=input_lang)
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
    elif cmd == 99:
        return translate_text("I didn't get that, please try again.", detect(translated_input))
    else:
        return "Unknown command."

def chat():
    kernel = setup_aiml()
    print("Hello! Ask me anything, or type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        user_lang = get_response_language(user_input)
        print(f"[Detected language: {user_lang}]")  

        translated_input = translate_text(user_input, 'en')

        answer = kernel.respond(translated_input)

        if answer.startswith('#'):
            response = process_commands(answer, translated_input)
        else:
            response = answer if user_lang == 'en' else translate_text(answer, dest_language=user_lang)

        print("Bot:", response)



if __name__ == "__main__":
    import sys
    user_input = sys.stdin.readline().strip()
    kernel = setup_aiml()
    user_lang = get_response_language(user_input)
    translated_input = translate_text(user_input, 'en')
    answer = kernel.respond(translated_input)
    
    if answer.startswith('#'):
        response = process_commands(answer, translated_input)
    else:
        response = answer if user_lang == 'en' else translate_text(answer, dest_language=user_lang)

    print(response)