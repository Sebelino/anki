import os
import tempfile

from elevenlabs import save
from elevenlabs.client import ElevenLabs


class Dupertts:
    def __init__(self):
        self.client = ElevenLabs(
            api_key=os.environ["ELEVENLABS_API_KEY"]
        )
        self.voice = "Emily"  # Genesis

    def generate(self, text: str) -> str:
        audio = self.client.generate(
            text=text,
            voice=self.voice,
            model="eleven_multilingual_v2",
        )
        path = tempfile.NamedTemporaryFile().name
        save(audio, path)
        return path


if __name__ == '__main__':
    tts = Dupertts()
    filename = tts.generate("test")
    print(filename)
