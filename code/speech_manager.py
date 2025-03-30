import pyttsx3
import markdown

class SpeechManager:
    def text_to_speech(self, text: str):
        try:
            tts_engine = pyttsx3.init()
            tts_engine.say(self._markdown_to_html(text))
            tts_engine.runAndWait()
        except Exception as error:
            print(f"Error during text-to-speech conversion: {error}")

    def _markdown_to_html(self, markdown_text: str) -> str:
        return markdown.markdown(markdown_text)
