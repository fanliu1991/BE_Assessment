#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json

MORTGAGE_INTEREST_RATE = 0.025
MIN_DOWN_PAYMENT_RATIO_FIRST_500K = 0.05
MIN_DOWN_PAYMENT_RATIO_OVER_500K = 0.1
NUMBER_OF_PAYMENT_PER_YEAR = {"weekly": 52, "biweekly": 26, "monthly": 12}


def minimum_down_payment_calculator(asking_price):
    """Calculate the minimum down payment based on the amount of mortgage.
    """
    if asking_price <= 500000:
        minimum_down_payment = asking_price * MIN_DOWN_PAYMENT_RATIO_FIRST_500K
    else:
        minimum_down_payment = 500000 * MIN_DOWN_PAYMENT_RATIO_FIRST_500K + (asking_price - 500000) * MIN_DOWN_PAYMENT_RATIO_OVER_500K
    return minimum_down_payment


def mortgage_insurance_calculator(down_payment, asking_price):
    """Calculate mortgage insurance based on the ration between down payment and the amount of mortgage.
    """
    down_payment_ratio = float(down_payment) / asking_price

    if down_payment_ratio >= 0.2 or asking_price > 1000000:
        mortgage_insurance = 0
    elif 0.15 <= down_payment_ratio < 0.2:
        mortgage_insurance = asking_price * 0.018
    elif 0.1 <= down_payment_ratio < 0.15:
        mortgage_insurance = asking_price * 0.024
    else:
        mortgage_insurance = asking_price * 0.0315
    return  mortgage_insurance


def payment_amount(request_json):
    """Get the recurring payment amount of a mortgage.

    Extract parameters from input json file and test whether parameters satisfy constraints or not.
    Calculate recurring payment amount based on payment formula.

    Params:
        request_json: A JSON consisting of asking price, down payment, payment schedule and amortization period.

    Returns:
        Payment amount per scheduled payment in JSON format,
        error information is included if occurred.

    Raises:
        ValueError: An error occurred if asking price, down payment or amortization period is not numerical value
        KeyError: An error occurred if payment schedule is not one of weekly, biweekly, monthly
    """

    try:
        request_parameter = json.loads(request_json)

        asking_price = float(request_parameter["asking price"])
        down_payment = float(request_parameter["down payment"])
        scheduled_payment_per_year = float(NUMBER_OF_PAYMENT_PER_YEAR[request_parameter["payment schedule"]])
        amortization_period = float(request_parameter["amortization period"])

        if asking_price < 0 or down_payment < 0 or (not 5 <= amortization_period <= 25):
            ret = {
                    "payment amount": "Error: given value is not allowed"
                }
            return json.dumps(ret)

        minimum_down_payment = minimum_down_payment_calculator(asking_price)
        if down_payment < minimum_down_payment:
            ret = {
                    "payment amount": "Error: minimum down payment is not satisfied"
                }
            return json.dumps(ret)

        mortgage_insurance = mortgage_insurance_calculator(down_payment, asking_price)
        scheduled_payment_times = amortization_period * scheduled_payment_per_year
        scheduled_payment_interest_rate = MORTGAGE_INTEREST_RATE / scheduled_payment_per_year

        payment_amount = ((asking_price - down_payment + mortgage_insurance) * 
        ((scheduled_payment_interest_rate * (1 + scheduled_payment_interest_rate) ** scheduled_payment_times) / 
                    ((1 + scheduled_payment_interest_rate) ** scheduled_payment_times - 1)))

        ret = {
                "payment amount": round(payment_amount, 2)
            }
        return json.dumps(ret)
    except ValueError as non_numerical_input:
        ret = {
                "payment amount": "Error: non-numerical values are given"
            }
        return json.dumps(ret)
    except KeyError as wrong_payment_schedule:
        ret = {
                "payment amount": "Error: payment schedule should be 'weekly', 'biweekly' or 'monthly'"
            }
        return json.dumps(ret)


def mortgage_amount(request_json):
    """Get the maximum mortgage amount.

    Extract parameters from input json file and test whether parameters satisfy constraints or not.
    Calculate the maximum mortgage amount based on payment formula.

    Params:
        request_json: A JSON consisting of payment amount, payment schedule and amortization period,
                      if down payment is included, its value should be added to the maximum mortgage returned.

    Returns:
        Maximum Mortgage that can be taken out in JSON format,
        error information is included if occurred.


    Raises:
        ValueError: An error occurred if payment amount, down payment or amortization period is not numerical value
        KeyError: An error occurred if payment schedule is not one of weekly, biweekly, monthly
    """

    try:
        request_parameter = json.loads(request_json)

        payment_amount = float(request_parameter["payment amount"])
        down_payment = float(request_parameter["down payment"] if "down payment" in request_parameter else 0)
        scheduled_payment_per_year = float(NUMBER_OF_PAYMENT_PER_YEAR[request_parameter["payment schedule"]])
        amortization_period = float(request_parameter["amortization period"])

        if payment_amount < 0 or down_payment < 0 or (not 5 <= amortization_period <= 25):
            ret = {
                    "mortgage amount": "Error: given value is not allowed"
                }
            return json.dumps(ret)

        scheduled_payment_times = amortization_period * scheduled_payment_per_year
        scheduled_payment_interest_rate = MORTGAGE_INTEREST_RATE / scheduled_payment_per_year

        mortgage_amount = (payment_amount / 
        ((scheduled_payment_interest_rate * (1 + scheduled_payment_interest_rate) ** scheduled_payment_times) / 
                    ((1 + scheduled_payment_interest_rate) ** scheduled_payment_times - 1)))

        ret = {
                "mortgage amount": round(mortgage_amount + down_payment, 2)
            }
        return json.dumps(ret)
    except ValueError as non_numerical_input:
        ret = {
                "mortgage amount": "Error: non-numerical values are given"
            }
        return json.dumps(ret)
    except KeyError as wrong_payment_schedule:
        ret = {
                "mortgage amount": "Error: payment schedule should be 'weekly', 'biweekly' or 'monthly'"
            }
        return json.dumps(ret)


def change_interest_rate(request_json):
    """Change the interest rate used by the application.

    Extract new interest rate from input json file and test whether it is available or not.
    Replace old interest rate with new interest rate.

    Params:
        request_json: A JSON consisting of new interest rate.

    Returns:
        Message indicating the old and new interest rate in JSON format,
        error information is included if occurred.

    Raises:
        ValueError: An error occurred if new interest rate is not numerical value.
    """
    try:
        request_parameter = json.loads(request_json)

        new_interest_rate = float(request_parameter["interest rate"]) / 100

        if new_interest_rate <= 0:
            ret = {
                    "old interest rate": MORTGAGE_INTEREST_RATE,
                    "new interest rate": "Error: negative interest rate is given"
                }
            return json.dumps(ret)

        global MORTGAGE_INTEREST_RATE
        old_interest_rate = MORTGAGE_INTEREST_RATE
        MORTGAGE_INTEREST_RATE = new_interest_rate

        ret = {
                "old interest rate": old_interest_rate,
                "new interest rate": MORTGAGE_INTEREST_RATE
            }
        return json.dumps(ret)
    except ValueError as non_numerical_input:
        ret = {
                "mortgage amount": "Error: non-numerical values are given"
            }
        return json.dumps(ret)


if __name__ == "__main__":
    payment_amount_input = {
        "asking price": 630000,
        "down payment": 300000,
        "payment schedule": "monthly",
        "amortization period": 10
        }
    payment_amount_json = json.dumps(payment_amount_input)
    payment = payment_amount(payment_amount_json)
    print payment, type(payment), "\n"

    mortgage_amount_input = {
        "payment amount": 3010,
        # "down payment": 300000,
        "payment schedule": "monthly",
        "amortization period": 10
        }
    mortgage_amount_json = json.dumps(mortgage_amount_input)
    mortgage = mortgage_amount(mortgage_amount_json)
    print mortgage, type(mortgage), "\n"

    interest_rate_input = {
        "interest rate": 12
        }
    interest_rate_json = json.dumps(interest_rate_input)
    interest_rate_message = change_interest_rate(interest_rate_json)
    print interest_rate_message, type(interest_rate_message), "\n"

    payment_amount_json = json.dumps(payment_amount_input)
    payment = payment_amount(payment_amount_json)
    print payment, type(payment), "\n"

    mortgage_amount_json = json.dumps(mortgage_amount_input)
    mortgage = mortgage_amount(mortgage_amount_json)
    print mortgage, type(mortgage), "\n"
