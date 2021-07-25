# Telegram messaging
import telepot
from telepot.loop import MessageLoop
import creds

def handle(msg):
    print(msg)

tankTOKEN = creds.botTanks
tankbot = telepot.Bot(tankTOKEN)
boilerTOKEN = creds.botBoiler
boilerbot = telepot.Bot(boilerTOKEN)

# #start the message bot
MessageLoop(tankbot, handle).run_as_thread()
MessageLoop(boilerbot, handle).run_as_thread()
print('Listening ...')
