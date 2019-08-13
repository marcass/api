# Telegram messaging
import telepot
import telepot.helper
from telepot.loop import MessageLoop
import telepot.api
import creds

def handle(msg):
    print(msg)

TOKEN = creds.botTanks
bot = telepot.Bot(TOKEN)

# #start the message bot
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
