from fastapi import APIRouter
from fastapi import Request, Form, File, UploadFile, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from core.config import AZURE_OPENAI_DEPLOYMENT,SPEECH_KEY,SPEECH_REGION,UPLOAD_FOLDER_PATH
from core.matrixEngine import MatrixGPT
import os
import json
import re
import sqlite3
import json
import string
import time
import threading
import wave

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA

import azure.cognitiveservices.speech as speechsdk


SPEECH_KEY=SPEECH_KEY
SPEECH_REGION=SPEECH_REGION

templates = Jinja2Templates(directory="templates")
general_pages_router = APIRouter()


@general_pages_router.get("/")
async def home(request: Request):
    print('HERE')
    return templates.TemplateResponse("general_pages/index.html",{"request":request})

@general_pages_router.get("/call")
async def home(request: Request):
    return templates.TemplateResponse("general_pages/call.html",{"request":request})


@general_pages_router.post("/summarychart")
async def summarychart(request: Request):
    print('in Summary Chart')
    plotlyCatDataArray=[]
    plotlySentimentDataArray=[]
    plotlyEmotionDataArray=[]
    plotlyAvgTimeDataArray=[]
    try:

        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('matrix.db')
        cursor = sqliteConnection.cursor()
       
        cursor.execute('''SELECT DISTINCT CATEGORY, COUNT(*) FROM transcript GROUP BY CATEGORY''')
        rows = cursor.fetchall()
        x=[]
        y=[]
        yValue=[]
        for row in rows:    
            title = row[0]
            x.append(title)     
            count = row[1]
            y.append(count)
            yValue.append(str(count))
             
        plotlyCatData={}
        plotlyCatData['x']=x
        plotlyCatData['y']=y
        plotlyCatData['type']='bar'
        plotlyCatData['text']=yValue
        plotlyCatData['textposition']='auto'
        
        plotlyCatDataArray.append(plotlyCatData)
        
        cursor.execute('''SELECT DISTINCT SENTIMENT, COUNT(*) FROM transcript GROUP BY SENTIMENT''')
        rows = cursor.fetchall()
        labels=[]
        values=[]
        for row in rows:    
            title = row[0]
            labels.append(title)     
            count = row[1]
            values.append(count)
             
        plotlySentimentData={}
        plotlySentimentData['labels']=labels
        plotlySentimentData['values']=values
        plotlySentimentData['type']='pie'
        
        plotlySentimentDataArray.append(plotlySentimentData)
        
        cursor.execute('''SELECT DISTINCT EMOTION, COUNT(*) FROM transcript GROUP BY EMOTION''')
        rows = cursor.fetchall()
        emotlabels=[]
        emotvalues=[]
        for row in rows:    
            title = row[0]
            emotlabels.append(title)     
            count = row[1]
            emotvalues.append(count)
             
        plotlyEmotionData={}
        plotlyEmotionData['labels']=emotlabels
        plotlyEmotionData['values']=emotvalues
        plotlyEmotionData['type']='pie'
        
        plotlyEmotionDataArray.append(plotlyEmotionData)
        
        cursor.execute('''SELECT DISTINCT CATEGORY, round(AVG(DURATION), 2) FROM transcript GROUP BY CATEGORY''')
        rows = cursor.fetchall()
        avgtimex=[]
        avgtimey=[]
        avgtimeyValue=[]
        for row in rows:    
            title = row[0]
            avgtimex.append(title)     
            count = row[1]
            avgtimey.append(count)
            avgtimeyValue.append(str(count))
             
        plotlyAvgTimeData={}
        plotlyAvgTimeData['x']=avgtimex
        plotlyAvgTimeData['y']=avgtimey
        plotlyAvgTimeData['type']='bar'
        plotlyAvgTimeData['text']=avgtimeyValue
        plotlyAvgTimeData['textposition']='auto'
        
        plotlyAvgTimeDataArray.append(plotlyAvgTimeData)
        
        cursor.close()
     
    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)

    # Close DB Connection irrespective of success
    # or failure
    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')
        
    return {"categoryresponse":plotlyCatDataArray,"sentimentresponse":plotlySentimentDataArray,"emotionresponse":plotlyEmotionDataArray,"avgtimeresponse":plotlyAvgTimeDataArray}


@general_pages_router.post("/createTranscript")
async def createTranscript(file: UploadFile = File(...)):
    recognized_text=[]
    #file.save(app.config['UPLOAD_FOLDER_PATH']+'datafile.pdf')
    with open(UPLOAD_FOLDER_PATH+file.filename, "wb+") as file_object:
        file_object.write(file.file.read())
    
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language="en-US"
    
    audio_config = speechsdk.audio.AudioConfig(filename=UPLOAD_FOLDER_PATH+file.filename)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    #speech_recognition_result = speech_recognizer.recognize_once_async().get()
    
    done = False
    
    def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
        print('Canceled event')

    def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStopped event')

    def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        #print('TRANSCRIBED:')
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            #print(evt.result.speaker_id+':'+evt.result.text)
            recognized_text.append(evt.result.speaker_id+':'+evt.result.text)
            #print('\tSpeaker ID={}'.format(evt.result.speaker_id))
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

    def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
        print('SessionStarted event')
    
    conversation_transcriber = speechsdk.transcription.ConversationTranscriber(speech_config=speech_config, audio_config=audio_config)

    transcribing_stop = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        #"""callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal transcribing_stop
        transcribing_stop = True

    # Connect callbacks to the events fired by the conversation transcriber
    conversation_transcriber.transcribed.connect(conversation_transcriber_transcribed_cb)
    conversation_transcriber.session_started.connect(conversation_transcriber_session_started_cb)
    conversation_transcriber.session_stopped.connect(conversation_transcriber_session_stopped_cb)
    conversation_transcriber.canceled.connect(conversation_transcriber_recognition_canceled_cb)
    # stop transcribing on either session stopped or canceled events
    conversation_transcriber.session_stopped.connect(stop_cb)
    conversation_transcriber.canceled.connect(stop_cb)

    conversation_transcriber.start_transcribing_async()

    # Waits for completion.
    while not transcribing_stop:
        time.sleep(.5)

    conversation_transcriber.stop_transcribing_async()
    final_transcript=''
    for record in recognized_text:
        final_transcript+=record+'\n'
    
    return {"response":final_transcript}

@general_pages_router.post("/generateInsights")
async def generateInsight(calltranscript: str= Form(...)):
    print('In Insights')
    insightsData = MatrixGPT.generateInsights(calltranscript)
    print(insightsData)
    
    return insightsData