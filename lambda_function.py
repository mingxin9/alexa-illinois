import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, request

from dining import get_hall_id
from answer import answer_entrees
from answer import answer_details

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def lambda_handler(event, _context):
    return ask.run_aws_lambda(event)


@ask.launch
def welcome():
    # init
    session.attributes['vegetarian'] = False
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("AMAZON.HelpIntent")
def help():
    help_msg = render_template('help')
    return question(help_msg)


@ask.intent("AMAZON.FallbackIntent")
def fallback():
    fallback_msg = render_template('error-not-understand')
    return question(fallback_msg)


@ask.intent("AMAZON.StopIntent")
def stop():
    goodbye_msg = render_template('goodbye')
    return statement(goodbye_msg)


@ask.intent("VegetarianIntent")
def vegetarian():
    if 'vegetarian' not in session.attributes.keys():
        session.attributes['vegetarian'] = True
    else:
        session.attributes['vegetarian'] = not session.attributes['vegetarian']
    vegetarian_msg = render_template('vegetarian')
    return question(vegetarian_msg)


@ask.intent("InteractiveIntent")
def interactive():
    session.attributes.pop('hall_id')
    session.attributes.pop('hall_name')
    session.attributes.pop('meal')
    session.attributes.pop('date')
    ask_hall_msg = render_template('inter-ask-hall')
    return question(ask_hall_msg)


@ask.intent("DetailIntent")
def detail():
    try:
        return answer_details(session.attributes['vegetarian'])
    except KeyError:
        err_msg = render_template('error-other')
        return statement(err_msg)


@ask.intent("AnswerHallIntent", mapping={'hall_name': 'hall'})
def answer_hall(hall_name):
    try:
        # get hall id from request
        hall = request.intent.slots.hall.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['id']
        # store hall id and name into session
        session.attributes['hall_id'] = get_hall_id(hall) 
        session.attributes['hall_name'] = hall_name
        # ask other not answered specs
        if 'hall_name' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-hall')
        elif 'meal' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-meal')
        elif 'date' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-date')
        else:
            return answer_entrees(session.attributes['vegetarian'])
        return question(ask_msg)
    except KeyError:
        ask_msg = render_template('error-not-understand')
        return question(ask_msg)


@ask.intent("AnswerMealIntent", mapping={'meal': 'meal'})
def answer_meal(meal):
    try:
        # get meal name from request
        meal = request.intent.slots.meal.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['id']
        # store meal into session
        session.attributes['meal'] = meal
        # ask other not answered specs
        if 'hall_name' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-hall')
        elif 'meal' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-meal')
        elif 'date' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-date')
        else:
            return answer_entrees(session.attributes['vegetarian'])
        return question(ask_msg)
    except KeyError:
        ask_msg = render_template('error-not-understand')
        return question(ask_msg)



@ask.intent("AnswerDateIntent", mapping={'date': 'date'})
def answer_date(date):
    try:
        # get date (today or tomorrow) from request
        date = request.intent.slots.date.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['id']
        # store date into session
        session.attributes['date'] = date
        # ask other not answered specs
        if 'hall_name' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-hall')
        elif 'meal' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-meal')
        elif 'date' not in session.attributes.keys():
            ask_msg = render_template('inter-ask-date')
        else:
            return answer_entrees(session.attributes['vegetarian'])
        return question(ask_msg)
    except KeyError:
        ask_msg = render_template('error-not-understand')
        return question(ask_msg)


@ask.intent("AskMainIntent", mapping={'hall_name': 'hall', 'meal': 'meal', 'date': 'date'})
def ask_main(hall_name, meal, date):
    try:
        # get all info from request
        hall = request.intent.slots.hall.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['id']
        meal = request.intent.slots.meal.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['id']
        date = request.intent.slots.date.resolutions.resolutionsPerAuthority[0]['values'][0]['value']['id']
        # store them in the session
        session.attributes['hall_id'] = get_hall_id(hall) 
        session.attributes['hall_name'] = hall_name
        session.attributes['meal'] = meal
        session.attributes['date'] = date
        return answer_entrees(session.attributes['vegetarian'])
    except KeyError:
        ask_msg = render_template('error-not-understand')
        return question(ask_msg)


if __name__ == '__main__':
    app.run(debug=True)