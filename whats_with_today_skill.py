""" This Alexa skill provides events that happened on this day in the past """

import random
import datetime

import requests
from bs4 import BeautifulSoup


def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.06b9b27e-3185-405f-9094-7dc7dd440319"):
        raise ValueError("Invalid Application ID")

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
    if intent_name == "WhatsUpIntent":
        return get_whatsupintent_response(intent, session)
    else:
        raise ValueError("Invalid intent")


def get_speech_output():
    """ Condenses multiple events into a single speech output """

    todays_events, source_url = get_todays_events_and_url()
    random_event = todays_events[random.randrange(0, len(todays_events))]

    speech_output = \
        "On this day in the year " + random_event['year'] + \
        ": " +  random_event['event']

    return speech_output, source_url


def get_whatsupintent_response(intent, session):
    """
    return list of news
    """
    session_attributes = {}
    reprompt_text = None

    speech_output, source_url = get_speech_output()
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, source_url, reprompt_text, should_end_session))


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
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Request trivia by saying whats interesting about today"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Request trivia by saying whats interesting about today"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, source_url, reprompt_text, should_end_session):
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
            'title': title,
            'content': output + "\n\nSource: " + source_url
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


def parse_event(event_string):
    """ Parses the event string into a better format """
    event_year, event = event_string.split(" – ", 1)
    # print(event_year, event)

    return {"year": event_year, "event": event}


def get_todays_events_and_url():
    """ Get the current day's events """

    today = datetime.datetime.now()
    month = today.strftime('%B')
    url = "https://en.wikipedia.org/wiki/" + month + "_" + str(today.day)

    response = requests.get(url, allow_redirects=True)

    document_soup = BeautifulSoup(response.content, 'html.parser')
    list_elements = document_soup.find(id="mw-content-text").findAll("ul")[1].findAll("li")

    list_elements = map(lambda x: BeautifulSoup(str(x), 'html.parser').get_text(), list_elements)
    events = list(map(parse_event, list_elements))

    return events, url


def main():
    """
    main function
    """
    print(get_speech_output())

if __name__ == '__main__':
    main()
