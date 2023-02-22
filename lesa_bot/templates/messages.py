GREETING_MESSAGE = """
Hello, I'm LESA! I provide an audio interface for practicing spoken English through communication with the GPT-3 AI DaVinci. The DaVinci model is capable of generating texts, understanding context, answering questions, and recognizing errors in the text.

   To start communicating, you need to go to the OpenAI page at the link below, register, and get an API key.\n
https://platform.openai.com/account/api-keys\n
   After registration, you are provided with the opportunity to use the API for free for 3 months with a limit on the number of words sent.
   Enter the command /set_key and send your API key to the bot. Now you can send the bot a voice message in English or a text message.

Commands:
/help - get information
/set_key - set OpenAI key
/set_text - setting for displaying text responses
/set_tts - selecting an engine for converting text to speech or disabling speech response
/set_mode - choosing a learning or free mode

From the developer.
   The developer is not responsible for any consequences of using this software.
   If you have any questions or suggestions regarding the operation and functionality of the bot, you can write them in the group https://t.me/LESAsupport
   This project is currently amateur and is provided "as is". The project uses third-party free solutions for speech recognition and text-to-speech conversion, the operation of which does not always produce the desired result.
In addition, ensuring high speed of such an application directly depends on the amount of money invested. If you use LESA, you could help support and develop the project. You will also help me and the project a lot if you find some regularly paid job for me :)
Help the project:
Sber:
2202200292158969

Commands:
/help - get information
/set_key - set OpenAI key
/set_text - setting for displaying text responses
/set_tts - selecting an engine for converting text to speech or disabling speech response
/set_mode - choosing a learning or free mode
"""

ACCAUNT_IS_NOT_EXIST = """
Your account was not found, please enter the command /start, then repeat the command /setkey to save the key.
"""

WRONG_DATA = """The entered data is not valid. Please enter the correct data or enter the command /cancel to cancel."""

SET_KEY_MESSAGE = """
/set_key:
Send your OpenAI API Key to save it.
You can get the key by going to the OpenAI website https://platform.openai.com/account/api-keys
\n\nIf you do not want to set the key now, enter /cancel.
"""

SET_TEXT_DISPLAY = """
/set_text:\n
Send 0 to not receive text responses.\n
Send 1 to receive text responses.\n
Send 2 to receive only bot responses.\n
Send 3 to receive only responses with the text of your recognized speech.\n\n
The default option is set to 1.
If you are communicating with the bot via text messages, only options 2 will be available.
Note that by opting out of text responses, you will receive a slight increase in the speed of delivery of voice responses. At the same time, it will be more difficult for you to control your speech.
\nIf you do not want to change the setting now, enter /cancel.
"""

SET_TTS_MESSAGE = """
/set_tts:\n
Send 0 if you do not want to receive the response as a voice message.

Send 1 to set up the use of another engine in case the first one does not respond within a few seconds (Google first - local backup). 

Send 2 to set up the use of another engine in case the first one does not respond within a few seconds (Local first - Google backup).

Send 3 if you want to use a local TTS engine to convert text to speech.

Send 4 if you want to use Google's TTS to convert text to speech.

The default option is set to 1.
Note a few nuances.
First, converting the response text to speech takes time.
Second, the third-party services used may not work fully stable. When using TTS provided by Google, the service's response to the request may take a long time and the request will have to be interrupted.
In the case of other engines used to convert text to speech, sometimes the result may be of poor quality or the request may not be executed.
\nIf you do not want to change the setting now, enter /cancel.
"""

SET_STT_MESSAGE = """
Currently, there is no possibility to use different speech-to-text engines no matter which option you choose.
"""

SET_MODE_MESSAGE = """
/set_mode: \n
You can choose between two conversation modes.\n
In Free mode, only your recognized speech or text message will be sent to the AI.
To select Free mode, send 0 \n\n
In Training mode, in addition to your speech, the AI will receive additional requests,
such as a command to check your speech for errors and ask you a question to maintain the conversation.
Please note that this mode will consume more OpenAI API tokens.
To select Training mode, send 1 \n\n
By default, option 1 is set.
\nIf you do not want to change the setting now, enter /cancel.
"""

HAVENOT_SETTINGS = """I'm sorry, but your account does not have 
an OpenAI API key, or your account settings are missing. You can get the OpenAI Key for free by registering 
at the link https://platform.openai.com/account/api-keys 
You can use the /help command for more information, or you can use the /set_key command to save OpenAI API key.
    """

HAVENOT_RECOGNIZED_TEXT = """Sorry, the speech recognition service could not recognize your speech or did not respond for a long time and recognition was stopped. Try again."""

