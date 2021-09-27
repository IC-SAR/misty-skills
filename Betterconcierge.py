import time
import random
import requests

from mistyPy.Robot import Robot
from mistyPy.Events import Events

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def bumper_pressed(event):
    is_contacted = event['message'].get('isContacted', False)
    bumper = event['message'].get('sensorId', None)

    if is_contacted:
        if bumper == 'brl':
            misty.DisplayImage("e_Joy.jpg")
            misty.MoveHead(yaw=0, roll=random.uniform(-50, 50))
            misty.Speak(('Hello! I am the NRD Conservation Program Virtual Assistant.'
                         '\n\nAsk me questions about the project!'),
                        speechRate=1.0,
                        utteranceId="Capture")
            time.sleep(.5)
            misty.MoveArm("left", -30)
            time.sleep(.5)
            misty.MoveArm("left", -10)
            time.sleep(.5)
            misty.MoveArm("left", -30)
        if bumper == 'brr':
            capture_speech()


def tts_done(event):
    uid = event['message'].get('utteranceId', None)
    print("Utterance ID:", uid)
    misty.DisplayImage("e_DefaultContent.jpg")
    misty.MoveArms(50, 50)

    if uid == "Capture":
        time.sleep(.5)
        capture_speech()


def capture_speech():
    misty.RegisterEvent("captureDone", Events.VoiceRecord, callback_function=capture_done)
    misty.CaptureSpeechAzure(True, 5000, 10000, False, False, 'en-us', '3cd713f1a1da48f08dc8710f306008a2',
                             'westcentralus')


def capture_done(event):
    srr = event['message'].get('speechRecognitionResult', None)
    if srr is None:
        srr = input("I didn't hear, please input manually: ")

    x = requests.post(
        ("https://api.us-south.assistant.watson.cloud.ibm.com/instances/4a3c0304-0432-41d3-a5c8-68ee155f1d28"
         "/v1/workspaces/24111c0c-5b6d-4d6b-a894-4b077066064c/message?version=2021-08-13"),
        None,
        {"input": {"text": srr}},
        headers={'Content-Type': 'application/json'},
        auth=("apikey", "vZRIptNPAzaQVA4b3SAMve0cnf81tdbjBZ8SezGWrAZ9")
    )
    text = x.json()['output']['generic'][0]['text']
    print(f"Heard: {x.json()['input']['text']}\nAnswered: {text}")
    process_watson(text)


def process_watson(text):
    if text == "I didn't get your meaning.":
        misty.DisplayImage("e_Disgust.jpg")
    misty.MoveArms(random.uniform(-30, 50), random.uniform(-30, 50))
    misty.MoveHead(yaw=0, roll=0)
    misty.Speak(text, utteranceId="NormalEyes")
    misty.Speak("Anything else I can answer?", utteranceId="NormalArms")


def stop_skill():
    misty.UnregisterAllEvents()


if __name__ == "__main__":
    misty = Robot("172.27.8.1")
    misty.RegisterEvent("TTSComplete", Events.TextToSpeechComplete, keep_alive=True, callback_function=tts_done)
    misty.RegisterEvent("bumperPressed", Events.BumpSensor, keep_alive=True, callback_function=bumper_pressed)
    misty.SetDefaultVolume(100)
