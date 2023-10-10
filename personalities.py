# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 16:05:21 2023

@author: James Wu
"""

import openai
import os

openai.api_key = "<API KEY HERE>"

def chatbot():
  messages = [{"role": "system", "content": "You are a sad assistant."},]

  while True:
    message = input("User: ")
    if message.lower() == "quit":
      break
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    chat_message = response['choices'][0]['message']['content']
    print(f"Bot: {chat_message}")
    messages.append({"role": "assistant", "content": chat_message})

if __name__ == "__main__":
  print("Start chatting with the bot (type 'quit' to stop)!")
  chatbot()
  
