from googletrans import Translator

translator = Translator()

def translate(text, dest='en', src='auto'):
    if (translator.detect(text)==dest): return text
    return translator.translate(text, dest=dest, src=src).text