from django.template import Library, loader

register = Library()


# https://stackoverflow.com/questions/42925233/sorting-based-on-hour-and-weekday
def weekday_sorter(dic):
    day = list(dic.keys())[0]
    return {'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 'THURSDAY': 4, 'FRIDAY': 5, 'SATURDAY': 6}[day]


def time_sorter(dic):
    hour_str = dic['time']
    hour = hour_str[:-2].replace(':', '0')
    am_pm = hour_str[-2:]
    return am_pm, int(hour)


def is_monday(session):
    return session['value']['day'] == 'MONDAY'


def is_tuesday(session):
    return session['value']['day'] == 'TUESDAY'


def is_wednesday(session):
    return session['value']['day'] == 'WEDNESDAY'


def is_thursday(session):
    return session['value']['day'] == 'THURSDAY'


def is_friday(session):
    return session['value']['day'] == 'FRIDAY'


def is_saturday(session):
    return session['value']['day'] == 'SATURDAY'


def filter_sessions(schedule, day):
    options = {'MONDAY': list(filter(is_monday, schedule)),
               'TUESDAY': list(filter(is_tuesday, schedule)),
               'WEDNESDAY': list(filter(is_wednesday, schedule)),
               'THURSDAY': list(filter(is_thursday, schedule)),
               'FRIDAY': list(filter(is_friday, schedule)),
               'SATURDAY': list(filter(is_saturday, schedule))}
    return options[day]


@register.inclusion_tag('classes/components/class_schedule.html', takes_context=True)
def render_schedule(context, schedule):

    weekdays_schedule = []

    for day in {'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'}:
        day_sessions = [d['value'] for d in filter_sessions(schedule.stream_data, day)]
        m_sche, tmp = {}, {}
        resultat = []
        for input in day_sessions:
            input['times'] = input['times'].split(';')
            for time in input['times']:
                resultat.append({'time': time, 'category': input['category']})
            m_sche[input['day']] = resultat
        tmp[day] = resultat
        weekdays_schedule.append(tmp)

    weekdays_schedule.sort(key=weekday_sorter)

    for dic in weekdays_schedule:
        for lst in list(dic.values()):
            lst.sort(key=time_sorter)

    return {'request': context['request'], 'schedule': schedule,
            'weekdays_schedule': weekdays_schedule}


'''@register.inclusion_tag('classes/components/class_schedule.html', takes_context=True)
def class_schedule(context):
    return {'request': context['request']}
'''


@register.filter(name='split')
def split(value):
    return value.split(';')