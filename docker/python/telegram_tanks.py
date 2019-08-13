# Telegram messaging
import telepot
import telepot.helper
from telepot.loop import MessageLoop
import telepot.api
import creds

def always_use_new(req, **user_kw):
    return None

def handle():
    print("got a message")

TOKEN = creds.botTanks
bot = telepot.Bot(TOKEN)

# #start the message bot
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
