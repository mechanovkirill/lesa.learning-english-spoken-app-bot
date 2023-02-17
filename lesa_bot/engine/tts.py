from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from gtts import gTTS
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor


def text_to_speech_coqui(text_: str) -> BytesIO:
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


async def text_to_speech_coqui_async(text_: str) -> BytesIO:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, text_to_speech_coqui, text_)
    return result


#  -----------------------------------------------------------------------------------------------------------
def text_to_speech_google(text_: str) -> BytesIO:
    answer = BytesIO()
    print('into gtts')
    gTTS(text=text_, lang='en').write_to_fp(answer)
    print('pass gtts')
    answer.seek(0)
    return answer


async def text_to_speech_google_async(text_: str) -> BytesIO:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, text_to_speech_google, text_)
    return result

# text = """In this example, the lang argument is set to 'es' for Spanish. You can replace 'es' with any supported
# language code to generate TTS audio in that language."""

# text_to_speech_coqui(text)


# async def text_to_speech_google_async(text_: str) -> BytesIO:
#     lang = 'en'
#     answer = BytesIO()
#     loop = asyncio.get_event_loop()
#     print('into gtts')
#     gtts = await loop.run_in_executor(None, gTTS, text_, lang)
#     rec = await loop.run_in_executor(None, gtts.write_to_fp, answer)
#     print('pass gtts')
#     rec.seek(0)
#     return rec
