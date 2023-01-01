import os
import mailbot
import time
import helpers
from dotenv import load_dotenv

load_dotenv()

chatId       = os.getenv('TG_CHAT_ID')
tgApiToken   = os.getenv('TG_API_TOKEN')
mailServer   = os.getenv('MAIL_SERVER')
mailAddress  = os.getenv('MAIL_ADDRESS')
mailPassword = os.getenv('MAIL_PASSWORD')
mailFolder   = os.getenv('MAIL_FOLDER')

mailbox = mailbot.Mailbox(mailServer, mailAddress, mailPassword, mailFolder)
sender  = mailbot.TgSender(tgApiToken, chatId)

print('Start checking..')
emails = mailbox.getUnseenMails()

print('Found ' + str(len(emails)) + ' new emails')
for email in emails:
  print(email)
  data = '*_New email received\!_*\n'
  data = data + '*To:* ' + helpers.escape_markdown(mailAddress, 2) + '\n'
  data = data + '*From:* ' +  helpers.escape_markdown(str(email['sender']), 2) + '\n'
  data = data + '*Subject:* ' +  helpers.escape_markdown(str(email['subject']), 2)

  print('data: ' + data)
  sender.send(data)
