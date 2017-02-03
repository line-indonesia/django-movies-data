import hmac
import hashlib
import base64
import json
import requests
import os
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from linebot import LineBotApi
from linebot.models import (TextSendMessage, ImageSendMessage, CarouselTemplate, CarouselColumn, TemplateSendMessage, MessageTemplateAction)
from linebot.exceptions import LineBotApiError

try:
    from app_properties import channel_secret, channel_access_token
except ImportError:
    channel_secret = os.environ['LINE_CHANNEL_SECRET']
    channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

# Create your views here.
@api_view(['POST'])
def callback(request):
    # Get request header and request body
    aXLineSignature = request.META.get('HTTP_X_LINE_SIGNATURE')
    print('Signature: ' + aXLineSignature)
    body = request.body
    print('Payload: ' + body)
    
    # Validate signature
    hash = hmac.new(channel_secret.encode('utf-8'),body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)
    
    # Exit when signature not valid
    if aXLineSignature != signature:
        return Response("X-Line-Signature is not valid")
    
    aPayload = json.loads(body)
    mEventType = aPayload['events'][0]['type']
    print('Event type: ' + mEventType)
    mSource = aPayload['events'][0]['source']['type']
    mReplyToken = aPayload['events'][0]['replyToken']

    if mEventType == 'join':
        if mSource == 'user':
            replyToUser(mReplyToken, 'Hello User')
        elif mSource == 'group':
            replyToUser(mReplyToken, 'Hello User')
        elif mSource == 'room':
            replyToUser(mReplyToken, 'Hello User')
        return Response("Event is join")

    if mEventType == 'message':
        if mSource == 'user':
            mTargetId = aPayload['events'][0]['source']['userId']
        elif mSource == 'group':
            mTargetId = aPayload['events'][0]['source']['groupId']
        elif mSource == 'room':
            mTargetId = aPayload['events'][0]['source']['roomId']

    mType = aPayload['events'][0]['message']['type']

    if mType != 'text':
        replyToUser(mReplyToken, 'Unknown message type')
        return Response("Message Type is not text")

    mText = aPayload['events'][0]['message']['text'].lower()

    if 'bot leave' in mText:
        botLeave(mTargetId, mSource)
        return Response("User want to exit")

    getMovieData(mText, mReplyToken, mTargetId)

    return Response ("Movies_Bot")


def getMovieData(text, reply_token, target_id):
    firstIndex = text.find('"', 0, len(text))
    lastIndex = text.rfind('"', 0, len(text))
    if firstIndex == lastIndex or firstIndex == -1 or lastIndex == -1:
        replyToUser(reply_token, 'Unknown keyword')
        return
    title = text[firstIndex+1:lastIndex]
    print('Title: ' + title)
    URI = 'http://www.omdbapi.com/?t=' + title + '&r=json'
    
    r = requests.get(URI)
    jResponse = r.json()
    print("OMDb responses: " + json.dumps(jResponse))

    msgToUser = ' '
    if 'title' in text:
        msgToUser = "Plot: " + jResponse['Plot'] + "\nReleased: " + jResponse['Released'] + "\nDirector: " + jResponse['Director'] + "\nWriter: " + jResponse['Writer'] + "\nAwards: " + jResponse['Awards'] + "\nActors: " + jResponse['Actors']
        pushImage(target_id, jResponse['Poster'])
    elif 'plot' in text:
        msgToUser = "Plot: " + jResponse['Plot']
    elif 'released' in text:
        msgToUser = "Released: " + jResponse['Released']
    elif 'poster' in text:
        pushImage(target_id, jResponse['Poster'])
        msgToUser = 'Poster for user'
    elif 'director' in text:
        msgToUser = "Director: " + jResponse['Director']
    elif 'writer' in text:
        msgToUser = "Writer: " + jResponse['Writer']
    elif 'awards' in text:
        msgToUser = "Awards: " + jResponse['Awards']
    elif 'actors' in text:
        msgToUser = "Actors: " + jResponse['Actors']
    elif 'carousel' in text:
        carousleForUser(jResponse['Poster'], target_id, jResponse['Title'])
        msgToUser = 'Carousel Template for user'

    print("Message to user: " + msgToUser)

    if len(msgToUser) <= 11 :
        replyToUser(reply_token, "Request Timeout");
    else:
        replyToUser(reply_token, msgToUser);

def replyToUser(reply_token, text_message):
    line_bot_api = LineBotApi(channel_access_token)
    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text_message))
    except LineBotApiError as e:
        print('replyToUser - Exception is raised ', str(e))

def pushImage(target_id, poster_url):
    line_bot_api = LineBotApi(channel_access_token)
    print('Poster URL: ' + poster_url)
    try:
        line_bot_api.push_message(target_id, ImageSendMessage(original_content_url=poster_url,
                                                              preview_image_url=poster_url))
    except LineBotApiError as e:
        print('pushImage - Exception is raised ', str(e))

def carousleForUser(poster_url, target_id, title):
    carousel_template = CarouselTemplate(columns=[
                                CarouselColumn(thumbnail_image_url=poster_url, title=title, text='Select one for more info', actions=[
                                        MessageTemplateAction(label='Full Data', text='Title \"'+title+'\"'),
                                        MessageTemplateAction(label='Summary', text='Plot \"'+title+'\"'),
                                        MessageTemplateAction(label='Poster', text='Poster \"'+title+'\"')
                                        ]),
                                CarouselColumn(thumbnail_image_url=poster_url, title=title, text='Select one for more info', actions=[
                                        MessageTemplateAction(label='Released Date', text='Released \"'+title+'\"'),
                                        MessageTemplateAction(label='Actors', text='Actors \"'+title+'\"'),
                                        MessageTemplateAction(label='Awards', text='Awards \"'+title+'\"')
                                        ])
                                ])
    template_message = TemplateSendMessage(alt_text='Your search result', template=carousel_template)
    line_bot_api = LineBotApi(channel_access_token)
    try:
        line_bot_api.push_message(target_id, template_message)
    except LineBotApiError as e:
        print('Exception is raised')

def botLeave(target_id, source_type):
    line_bot_api = LineBotApi(channel_access_token)
    try:
        if source_type == 'room':
            line_bot_api.leave_room(target_id)
        elif source_type == 'group':
            line_bot_api.leave_group(target_id)
    except LineBotApiError as e:
        print('Exception is raised')







