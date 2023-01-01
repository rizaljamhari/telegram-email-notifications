import os
import imaplib
import re
import email.header
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class Mailbox:
  def __init__(self, mail, mailbox, password, folder = 'Inbox'):
    if not mail or not mailbox or not password:
      raise Exception('Each parameter must not be empty')
    self.mail = mail
    self.mailbox = mailbox
    self.__password = password
    self.folder = folder
    self.__login()

  def __login(self):
    try:
      self.__imap = imaplib.IMAP4_SSL(self.mail)
      self.__imap.login(self.mailbox, self.__password)
      uids = self.__getUnseenUids()
    except:
      raise Exception('Access denied. Check the data or the server permissions.')

  def getUnseenMails(self):
    uids = self.__getUnseenUids()

    if len(uids) == 0:
      return []

    mails = []

    for uid in uids:
      print('Checking ' + str(uid) + ' Notification sent?: ' + str(self.__isNotificationSent(uid)))
      if self.__isNotificationSent(uid):
        continue

      mail = {}
      try:
        tmp, text = self.__imap.uid('fetch', str(uid).encode('utf-8'), '(FLAGS RFC822.HEADER)')
        text = text[0][1].decode()
      except:
        continue
      else:
        # An easier way to get sender and subject is to use mail.parser.Parser
        mail['sender'] = self.__extractMailData(text, '\r\nFrom: (.*?)\r\n[\w]')
        mail['subject'] = self.__extractMailData(text, '\r\nSubject: (.*?)\r\n[\w]')
        mails.append(mail)

        # write to file to avoid sending the same notification twice
        with open('notificationSent.txt', 'a') as notificationSentFile:
          notificationSentFile.write(str(uid) + '\n')

    return mails

  def __extractMailData(self, source, regex):
    result = ''
    try:
      data = re.search(regex, source, re.DOTALL)
      data = data.group(1)
      data = email.header.decode_header(data)
      for d in data:
        try:
          result += d[0].decode()
        except:
          result += d[0]
    except:
      result = ''
    finally:
      return result

  def __getUnseenUids(self):
    try:
      self.__imap.select(self.folder)
      result, uids = self.__imap.uid('search', None, "UNSEEN")
      uids = uids[0].decode().split(' ')
      uids = [int(uid) for uid in uids]
    except:
      return []
    else:
      return uids

  def __isNotificationSent(self, uid):
    with open('notificationSent.txt') as notificationSentFile:
      if str(uid) in notificationSentFile.read():
        return True

    return False

class TgSender:

  __sendMessageUrl = 'https://api.telegram.org/bot<token>/sendMessage'

  def __init__(self, token, chatId):
    if not token or not chatId:
      raise Exception('Each parameter must not be empty')
    self.__tgApiToken = token
    self.__sendMessageUrl = self.__sendMessageUrl.replace('<token>', token)
    self.__chatId = chatId

  def send(self, text):
    print('text: ' + text)
    data = {
      'chat_id': self.__chatId,
      'text': text,
      'parse_mode': 'MarkdownV2',
      'reply_markup': json.dumps({
        "inline_keyboard": [[
          { "text": "Open Webmail", "url": os.getenv('MAIL_CLIENT_URL') }
        ]]
      })
    }

    try:
      r = requests.post(self.__sendMessageUrl, data=data)
    except:
      print('Failed to send notification. Check the availability of Telegram servers (for example, Telegram website) from place where the script is running')
