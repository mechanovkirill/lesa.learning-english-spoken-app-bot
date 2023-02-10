# import all the modules that we will need to use
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from gtts import gTTS
from io import BytesIO


def text_to_speech_coqui(text_) -> BytesIO:
    path = "/home/certo/lesa/venv/lib/python3.10/site-packages/TTS/.models.json"
    model_manager = ModelManager(path)
    model_path, config_path, model_item = model_manager.download_model("tts_models/en/ljspeech/tacotron2-DDC")
    voc_path, voc_config_path, _ = model_manager.download_model(model_item["default_vocoder"])

    syn = Synthesizer(
        tts_checkpoint=model_path,
        tts_config_path=config_path,
        vocoder_checkpoint=voc_path,
        vocoder_config=voc_config_path
    )

    outputs = syn.tts(text_)
    answer = BytesIO()
    syn.save_wav(outputs, answer)
    return answer


def text_to_speech_google(text_) -> BytesIO:
    # Initialize gTTS
    answer = BytesIO()
    print('into gtts')
    gTTS(text=text_, lang='en').write_to_fp(answer)
    print('pass gtts')
    answer.seek(0)
    return answer


# text = """In this example, the lang argument is set to 'es' for Spanish. You can replace 'es' with any supported
# language code to generate TTS audio in that language."""

# text_to_speech_coqui(text)
