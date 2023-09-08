<h1 align="center"> Lumo </h1>

<p align="center">
  <img width=240 src="logo.png" alt="Logo"/>
</p>

## About ##

  Lumo is an open-source, localhosted voice assistant similar to Alexa or Google Home. Currently it is capable of generally responding to information, searching wikipedia for information, sending text messages, getting the weather, finding nearby buisnesses, and much more. 

## Goals ##

  Currently Lumo is still under active development, but there are a few long term goals being worked towards.
  
  1. Locally hosting the speech to text, LLM, and voice. <br>
    Currently all of these rely on a third party API, which is both the biggest cost as well as the least private aspect of Lumo.
  2. Rework some current features. <br>
    There are several features that are functional but could be improved. These include data syncing between instances of Lumo hosted on the same network, SMS responsing, and music playback
  3. Continue implementing new features. <br>
    Lumo is still being actively worked on and improved, and new features are being implemented, including events, reminders, and much more

## Installation ##
  
  A smooth installation experience is very important, and this is one of the features being actively improved. In the mean time, here are the instructions to install this project on your local machine.
  1. Make sure you have python installed. <br>
    The latest version of python is available here: https://www.python.org/downloads/
  2. Clone the repository to your local device. <br>
    This can be done in one of 2 ways: <br>
      - Run the following command: ```git clone https://github.com/LukeS26/Lumo.git```
      - Click the green Code button and download the zip file.
  3. Install the required libraries: <br>
     At the moment this takes a long time, as I believe many of the requirements aren't necessary. This is one of the aspects of the install being worked on.
       - Run the following command: ```pip install -r requirements.txt```
  4. Open and modify the config_variables.py file: <br>
    This is by far the most complicated part of the setup, as it requires getting API keys for several services:
       - Twilio
       - OpenAI
       - Eleven Labs
       - Google Search
       - Google Locations
       - Open Weather Map
      <br>
        After getting these keys, you can also specifiy your name, which room the assistant is set up in, your location, and your contact's names and phone numbers.<br>
        Please note that these details are not shared with any external service besides the single API that needs them.
  5. Launch the Assistant<br>
     Now the assistant can be launched.
       - Run the following commands: <br>
         ```cd Lumo```<br>
       ```py .\launcher.py```
