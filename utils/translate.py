from googletrans import Translator

translator = Translator()

def translate(text, dest='en', src='auto'):
    return translator.translate(text, dest=dest, src=src).text