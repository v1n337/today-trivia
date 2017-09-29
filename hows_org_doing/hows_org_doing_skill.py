"""
This Alexa skill provides the general sentiment about a company
on Twitter since a given date
"""

import random
import json
import functools
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup
import twitter
import preprocessor
import isodate
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SENTIMENT_TIER_1_UB = -0.6
SENTIMENT_TIER_2_UB = -0.2
SENTIMENT_TIER_3_UB = 0.2
SENTIMENT_TIER_4_UB = 0.6


def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.ask.skill.06b9b27e-3185-405f-9094-7dc7dd440319"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "HowsTheOrgIntent":
        return get_howstheorgintent_response(intent, session)
    else:
        raise ValueError("Invalid intent")



def get_tweets_about_org(orgname, date_from):
    """ Get tweets from a given date about an organization """

    api = twitter.Api(consumer_key='pnQFCZpsEfUxdmCOXiOYgEQDA',
                      consumer_secret='lbnlPekP1lNIODvC4U8lwOnlO8r2MFPAr8VpnL2JYM4TL94MGE',
                      access_token_key='218891284-vDatV2MOCc8j0MdVmHnZM40tZmfaymgUOZEKnYhC',
                      access_token_secret='lWeGDsq9FUL8uGaYb4JkQ2kXllH2mx3jbtG4sdPS3059L')

    tweets_objects = api.GetSearch(
        term=orgname,
        count=100,
        result_type="recent",
        lang="en",
        since=date_from)

    tweets = list(map(lambda x: x.text, tweets_objects))
    cleaned_tweets = list(map(preprocessor.clean, tweets))
    print(cleaned_tweets)

    return cleaned_tweets

def get_general_sentiment_from_tweets(tweets):
    num_tweets = len(tweets)
    analyzer = SentimentIntensityAnalyzer()

    polarity_scores = list(map(analyzer.polarity_scores, tweets))
    sentiment_scores = list(map(lambda x: x['compound'], polarity_scores))
    aggregated_sentiment_score = functools.reduce(lambda x, y: x + y, sentiment_scores, 0) / num_tweets

    print("aggregated_sentiment_score ", aggregated_sentiment_score)

    return aggregated_sentiment_score


def get_speech_output(orgname, date_from):
    """ Condenses multiple events into a single speech output """

    org_tweets = get_tweets_about_org(orgname, date_from)
    sentiment_score = get_general_sentiment_from_tweets(org_tweets)

    speech_output = \
        "The general public sentiment for " + orgname

    if sentiment_score > SENTIMENT_TIER_4_UB:
        speech_output += " has been overwhelmingly positive"
    elif sentiment_score > SENTIMENT_TIER_3_UB:
        speech_output += " has been moderately positive"
    elif sentiment_score > SENTIMENT_TIER_2_UB:
        speech_output += " has been neutral"
    elif sentiment_score > SENTIMENT_TIER_1_UB:
        speech_output += " has been moderately negative"
    else:
        speech_output += " has been overwhelmingly negative"

    return speech_output


def get_howstheorgintent_response(intent, session):
    """
    return the general sentiment
    """
    session_attributes = {}
    reprompt_text = None

    orgname = intent['slots']['orgname']['value']
    date_from_str = intent['slots']['datefrom']['value']

    date_from = isodate.parse_date(date_from_str)
    today_date = date.today()

    while date_from > today_date:
        date_from -= timedelta(days=365)

    print(orgname)
    print(date_from)

    speech_output = get_speech_output(orgname, str(date_from))
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """
    If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills for public organization sentiment \
                    For instance, you can request the sentiment about Amazon since September 1st, 2017 \
                    by saying hows amazon doing since September 1st, 2017?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can request the sentiment about an organization, say Amazon, \
                    since September 1st, 2017 by saying hows amazon doing since September 1st, 2017?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    '''
    @return: speechlet dict
    '''
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    '''
    @return: skill final response
    '''
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def main():
    """
    main function
    """
    print(get_speech_output("twitter", "2017-09-01"))

if __name__ == '__main__':
    main()
