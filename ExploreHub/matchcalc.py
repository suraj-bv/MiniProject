from datetime import datetime


def cal_dates(me, my_trip, pal, pal_trip):
    start1 = datetime.strptime(str(my_trip.start_date), "%Y-%m-%d")
    end1 = datetime.strptime(str(my_trip.end_date), "%Y-%m-%d")
    start2 = datetime.strptime(str(pal_trip.start_date), "%Y-%m-%d")
    end2 = datetime.strptime(str(pal_trip.end_date), "%Y-%m-%d")

    latest_start, earliest_end = max(start1, start2), min(end1, end2)
    return max((earliest_end - latest_start).days + 1, 0)


def calc_age(me, my_trip, pal, pal_trip):
    score_mapping = [
        {"start": 0, "end": 5, "score": 20},
        {"start": 6, "end": 10, "score": 10},
        {"start": 11, "end": 50, "score": 4}
    ]

    my_date_of_birth = datetime.strptime(str(me.date_of_birth), "%Y-%m-%d")
    pal_date_of_birth = datetime.strptime(str(pal.date_of_birth), "%Y-%m-%d")
    difference = abs((my_date_of_birth - pal_date_of_birth).days) / 365

    for details in score_mapping:
        if details["start"] <= difference <= details["end"]:
            return details["score"]

    return 0


def calc_characteristics(me, my_trip, pal, pal_trip):
    score = 0
    score += 10 if me.financial_nature == pal.financial_nature else 0
    score += 10 if my_trip.nature_trip == pal_trip.nature_trip else 0
    score += 5 if me.dietary_restrictions == pal.dietary_restrictions else 0
    score += 5 if my_trip.trip_preferences == pal_trip.trip_preferences else 0

    return score


def calc_match_score(me, my_trip, pal, pal_trip):
    calc_functions = [cal_dates, calc_age, calc_characteristics]
    total_score = 0
    for function in calc_functions:
        total_score += function(me, my_trip, pal, pal_trip)
    return total_score
