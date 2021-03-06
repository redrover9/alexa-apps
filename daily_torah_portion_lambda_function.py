# -*- coding: utf-8 -*-
import logging
import requests
import json
import datetime
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to the Daily Torah Portion Alexa Skill. You can ask me for the daily portion."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class DailyPortionHandler(AbstractRequestHandler):
# The intent reflector is used for interaction model testing and debugging.
  #  It will simply repeat the intent the user said. You can create custom handlers
   # for your intents by defining them above, then also adding them to the request
    # handler chain below.

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        if ask_utils.is_request_type("dailyPortion"):
            return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        url = "http://www.sefaria.org/api/calendars/?timezone=America/Vancouver&custom=ashkenazi"
        response = requests.get(url).json()
        sefaria_info = response
        todays_weekday = datetime.date.today().isoweekday()
        todays_aliyah = (sefaria_info['calendar_items'][0]['extraDetails']['aliyot'][todays_weekday])
        todays_aliyah_url = todays_aliyah.replace(" ", ".")
        todays_aliyah_url = 'https://www.sefaria.org/api/texts/' + todays_aliyah_url + '?context=0'
        
        reading_response = requests.get(todays_aliyah_url).json()
        reading_text = (reading_response['text'])
        reading_text = ''.join(str(reading_text)[1:-1])
        reading_text = str(reading_text)
        reading_text = reading_text.replace("<i>", "")
        reading_text = reading_text.replace("</i>", "")
        
        speech = todays_aliyah + reading_text
        handler_input.response_builder.speak(speech).ask(speech)

        speak_output = "Today's portion is " + speech

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
                

        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say tell me the daily portion! How can I help you?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .set_should_end_session(False)
                .response
                
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
# The intent reflector is used for interaction model testing and debugging.
  #  It will simply repeat the intent the user said. You can create custom handlers
   # for your intents by defining them above, then also adding them to the request
    # handler chain below.

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(DailyPortionHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
