from html import unescape
from time import time
from sys import argv
import csv
import os
import re
from langdetect import detect

class Message:
    def __init__(self):
        self.messageID = None
        self.timestamp = None
        self.sender = None
        self.fwd = None
        self.reply = None
        self.content = None

    def toTuple(self):
        if self.messageID: self.messageID = self.messageID.replace("message", "")
        if self.sender: self.sender = unescape(self.sender.strip())
        if self.fwd: self.fwd = unescape(self.fwd.strip())
        if self.reply: self.reply = self.reply.replace("message", "")
        if self.content: self.content = unescape(self.content.strip())

        return (self.messageID, self.timestamp, self.sender, self.fwd, self.reply, self.content)

class GetData:

  def __init__(self):
    self.messageIDNewPattern = re.compile('<div class="message default clearfix" id="([^"]+)')
    self.messageIDJoinedPattern = re.compile('<div class="message default clearfix joined" id="([^"]+)')
    self.timestampPattern = re.compile('<div class="pull_right date details" title="([^"]+)')
    self.fwdPattern = re.compile('<div class="userpic userpic\d+" style="width: 42px; height: 42px">')
    self.fwdSenderPattern = re.compile('([^<]+)<span class="details"> ')
    self.sameFWDMediaPattern = re.compile('<div class="media_wrap clearfix">')
    self.sameFWDTextPattern = re.compile('<div class="text">')
    self.replyPattern = re.compile('In reply to <a href="(?:messages\d*.html)?#go_to_([^"]+)"')

    self.photoPattern = re.compile('<div class="media clearfix pull_left media_photo">')
    self.videoPattern = re.compile('<div class="media clearfix pull_left media_video">')
    self.voicePattern = re.compile('<div class="media clearfix pull_left media_voice_message">')
    self.audioPattern = re.compile('<div class="media clearfix pull_left media_audio_file">')
    self.filePattern = re.compile('<div class="media clearfix pull_left media_file">')
    self.contactPattern = re.compile('<div class="media clearfix pull_left media_contact">')
    self.contactLinkPattern = re.compile('<a class="media clearfix pull_left block_link media_contact" href="[^"]+"')
    self.locationLinkPattern = re.compile('<a class="media clearfix pull_left block_link media_location" href="[^"]+"')
    self.callPattern = re.compile('<div class="media clearfix pull_left media_call( success)?">')
    self.pollPattern = re.compile('<div class="media_poll">')
    self.gamePattern = re.compile('<a class="media clearfix pull_left block_link media_game" href="[^"]+">')
    self.linkHTMLPattern = re.compile('</?a[^<]*>')
    self.htmlTags = ["em", "strong", "code", "pre", "s"]
    self.t0 = time()

  def extract_videos(self,text):
    search = 'Video|Vimeo|vimeo'
    try:
      result = re.findall(search, text,flags=re.IGNORECASE)
      if len(result)>=1:
        return "Video"
      else:
        return ""
    except Exception as e:
      return ""

  def extract_photo(self,text):
    search = 'Photo|.png|.jpg'
    try:
      result = re.findall(search, text,flags=re.IGNORECASE)
      if len(result)>=1:
        return "Photo"
      else:
        return ""
    except Exception as e:
      return ""

  def extract_audio(self,text):
    search = 'Audio file'
    try:
      result = re.findall(search, text,flags=re.IGNORECASE)
      if len(result)>=1:
        return "Audio File"
      else:
        return ""
    except Exception as e:
      return ""

  def extract_doc(self,text):
    search = '.pdf|doc|docx'
    try:
      result = re.findall(search, text,flags=re.IGNORECASE)
      if len(result)>=1:
        return "Documents"
      else:
        return ""
    except Exception as e:
      return ""

  def check_statement(self,text):
    try:
      result = re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text)
      if len(result)>=60:
        return "Statement / Press release"
    except Exception as e:
      return ""


  def language_detection(self,x):
    try:
      x = detect(x)
      if x=='en':
        x='English'
      elif x=='ur'or x=='fa':
        x="Urdu"
      else:
        x=''
    except:
      x = ''
    return x

  def extract_url(self,text):
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', str(text))
    if len(urls)>1:
      return urls[0]
    else:
      return ""
      

    

  def get_data(self,file):
    print("Starting...")

    # Scans current directory for message<n>.html Telegram chat export files
    messageFiles = []
    n = 1
    # for file in os.listdir():
    #     if file.startswith("messages") and file.endswith(".html"):
    #         messageFiles.append("messages" + (str(n) if n > 1 else "") + ".html")
    #         n += 1
    messageFiles = file
    
    if not messageFiles:
        print("No message.html files found. Are you sure the script is in the right directory? Exiting...")
        exit()

    print("Loading all {} message files...".format(len(messageFiles)))
    print("message files",messageFiles)
    print("Static path")

    # Loads all files content into memory
    lines = []
    for file in messageFiles:
        with open(file, encoding="UTF-8") as f:
            lines += [line.replace("\n", "").strip() for line in f if line.strip()]
    # Sets output filename as the chat's name
    chatName = lines[15]
    outputFile = "Telegram-" + "".join(c if c.isalnum() else "_" for c in chatName) + ".csv"

    print("Processing '{}'...".format(chatName))
    messages = []
    cur = 0
    lastSender = None
    lastFWDSender = None

    while cur < len(lines):
      # Skip lines that aren't the start of a message
      if not lines[cur].startswith("<div class="):
          cur += 1
          continue

      # Check if it's a new sender's message
      new = True
      messageID = re.findall(self.messageIDNewPattern, lines[cur])
      if not messageID:
          new = False
          messageID = re.findall(self.messageIDJoinedPattern, lines[cur])

      # Skip lines that aren't the start of a message
      if not messageID:
          cur += 1
          continue
      
      m = Message()
      m.messageID = messageID[0]

      if new: # New sender
        # If it's from a Deleted Account, no initial is
        # shown as avatar, so there's a line less to skip
        if lines[cur+4] == "</div>":
            cur += 8
        else:
            cur += 9

        timestamp = re.findall(self.timestampPattern, lines[cur])
        m.timestamp = timestamp[0]

        cur += 4
        m.sender = lines[cur]
        lastSender = m.sender

        cur += 3
        m.content = lines[cur]
      else: # Same sender as the message before
          cur += 2
          timestamp = re.findall(self.timestampPattern, lines[cur])
          m.timestamp = timestamp[0]

          m.sender = lastSender

          cur += 4
          m.content = lines[cur]
      
      isFWD = re.match(self.fwdPattern, m.content)
      isSameFWDText = re.match(self.sameFWDTextPattern, m.content)
      isSameFWDMedia = re.match(self.sameFWDMediaPattern, m.content)
      isReply = re.findall(self.replyPattern, m.content)

      if isFWD:
        # If it's from a Deleted Account, no initial is
        # shown as avatar, so there's a line less to skip
        if lines[cur+2] == "</div>":
            cur += 7
        else:
            cur += 8
        
        fwdSender = re.findall(self.fwdSenderPattern, lines[cur])
        m.fwd = fwdSender[0]
        lastFWDSender = m.fwd

        cur += 3
        m.content = lines[cur]
      elif isSameFWDText:
        m.fwd = lastFWDSender

        cur += 1
        m.content = lines[cur]
      elif isSameFWDMedia:
          m.fwd = lastFWDSender

          cur += 6
          m.content = "["+lines[cur]+"]"
      elif isReply:
          m.reply = isReply[0]

          cur += 3
          m.content = lines[cur]
      
      if m.content.startswith("<"):
          isPhoto = re.match(self.photoPattern, m.content)
          isVideo = re.match(self.videoPattern, m.content)
          isVoice = re.match(self.voicePattern, m.content)
          isAudio = re.match(self.audioPattern, m.content)
          isFile = re.match(self.filePattern, m.content)
          isContact = re.match(self.contactPattern, m.content)
          isContactLink = re.match(self.contactLinkPattern, m.content)
          isLocationLink = re.match(self.locationLinkPattern, m.content)
          isCall = re.match(self.callPattern, m.content)
          isPoll = re.match(self.pollPattern, m.content)
          isGame = re.match(self.gamePattern, m.content)

          # Write type of media as content
          if any([isPhoto, isVideo, isVoice, isAudio, isFile]):
              cur += 5
              m.content = "["+lines[cur]+"]"
          elif isContact or isContactLink:
              cur += 5
              m.content = "[Contact - "+lines[cur]+" - "+lines[cur+3]+"]"            
          elif isLocationLink:
              cur += 5
              m.content = "["+lines[cur]+" - "+lines[cur+3]+"]"
          elif isCall:
              cur += 8
              m.content = "[Call - "+lines[cur]+"]"
          elif isPoll:
              m.content = "["+lines[cur+5]+" - "+lines[cur+2]+"]"
          elif isGame:
            m.content = "[Game - "+lines[cur+5]+" - "+lines[cur+11]+"]"  

      if "<br>" in m.content:
        m.content = m.content.replace("<br>", "\\n")
      
      # Remove HTML formatting tags
      if "<" in m.content:
          for original in self.htmlTags:
              m.content = m.content.replace("<"+original+">", "")
              m.content = m.content.replace("</"+original+">", "")

      # Remove <a> tags
      if "<a" in m.content:
          m.content = re.sub(self.linkHTMLPattern, "", m.content)

      # Handle animated emojis, as they're not logged properly by Telegram (might change soon?)
      if m.content == "</div>":
          m.content = "[Animated emoji]"

      messages.append(m)
      cur += 1
    

    # Write CSV
    with open(outputFile, "w+", encoding="UTF-8", newline="") as f:
        csv.writer(f).writerows([m.toTuple() for m in messages])

    print("Written to '{}' in {:.2f}s.".format(outputFile, time()-self.t0))
    import pandas as pd
    names = ['Timestamp','Account',"Nan1","Nan2","Post"]
    data = pd.read_csv(outputFile,  usecols=range(1,6),header=None,names=names)
    data['Statement / Press release'] = data['Post'].apply(self.check_statement)
    data['Photo'] = data['Post'].apply(self.extract_photo)
    data['Video'] = data['Post'].apply(self.extract_videos)
    data['Audio File'] = data['Post'].apply(self.extract_audio)
    data['Language'] = data['Post'].apply(self.language_detection)
    data['Documents'] = data['Post'].apply(self.extract_doc)
    data["URLS"] = data['Post'].apply(self.extract_url)
    data = data.drop(columns=['Nan1',"Nan2"])
    return data,outputFile
        
        






