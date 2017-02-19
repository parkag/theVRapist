import os
from gtts import gTTS
import speech_recognition as sr

r = sr.Recognizer()


class TerminalInterface:

    def get_user_input(self):
        text = input()
        return text

    def get_user_output(self, response):
        print(response)


class AudioInterface:

    def __init__(self, input_lang, output_lang):
        self.input_lang = input_lang
        self.output_lang = output_lang

    def get_user_input(self):
        print("Say something!")
        audio = self._get_audio()
        print('got audio')
        text = self._transcribe(audio)
        print("Understood: " + text)
        return text

    def get_user_output(self, response):
        print("Response: " + response)
        self._read_text(response)

    def _get_audio(self):
        with sr.Microphone() as source:
            audio = r.listen(source)
        return audio

    def _transcribe(self, audio):
        """Turn audio into text"""
        try:
            user_input = remove_punct(
                r.recognize_google(audio, language=self.input_lang).upper()
            )
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except:
            print('Exception occurred')
        return user_input

    def _read_text(self, text):
        tts = gTTS(text=text, lang=self.output_lang)
        tts.save("response.mp3")
        os.system("mpg321 response.mp3 --quiet")
        os.system('rm response.mp3')


def remove_punct(string):
    """Remove common punctuation marks."""
    if string.endswith('?'):
        string = string[:-1]
    return (string.replace(',', '')
            .replace('.', '')
            .replace(';', '')
            .replace('!', ''))
