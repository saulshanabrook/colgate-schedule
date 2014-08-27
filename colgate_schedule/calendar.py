import datetime
import bs4
import ics
import requests
import itertools
import pytz


def daterange(start_date, end_date):
    '''
    from http://stackoverflow.com/a/1060330/907060
    '''
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


FIRST_DAY_OF_CLASSES = datetime.date(2014, 8, 30)
LAST_DAY_OF_CLASSES = datetime.date(2015, 5, 1)
DAYS_WITH_NO_CLASSES = list(itertools.chain.from_iterable([
    # Mid-Term Recess
    daterange(datetime.date(2014, 10, 11), datetime.date(2014, 10, 14)),
    # Thanksgiving Recess
    daterange(datetime.date(2014, 11, 22), datetime.date(2014, 10, 30)),
    # winter break
    daterange(datetime.date(2014, 12, 13), datetime.date(2015, 1, 18)),
    # mid-term recess
    daterange(datetime.date(2015, 3, 14), datetime.date(2015, 3, 22))
]))


def get_school_days():
    for date in daterange(FIRST_DAY_OF_CLASSES, LAST_DAY_OF_CLASSES):
        if date not in DAYS_WITH_NO_CLASSES:
            yield date


def login_to_portal(session, username, password):
    LOGIN_URL = 'https://cas.colgate.edu/cas/login'

    # to get sessions id cookies `JSESSIONID`
    r = session.get(LOGIN_URL)
    session_id = session.cookies['JSESSIONID']

    # to get hidden lt value that needs to be sent with form
    soup = bs4.BeautifulSoup(r.text)
    lt = soup.find('input', attrs={'name': "lt"})['value']

    # to login
    post_url = LOGIN_URL + ';jsessionid=' + session_id
    data = {
        'username': username,
        'password': password,
        'lt': lt,
        'execution': 'e1s1',
        '_eventId': 'submit',
    }
    r = session.post(post_url, data=data)


def parse_time(date_text, force_pm=False):
    '''
    parses a time text like 1:00, and infers whether it is morning or night.
    If it before 9:00, or `force_pm` if True, then PM, otherwise, AM.

    If it is `TBA`, will return None
    '''
    if date_text == 'TBA':
        return None
    hour, minute = map(int, date_text.split(':'))

    # if it is before 9:00 assume it is afternoon, not morning
    if force_pm or (hour < 9):
        hour += 12
    return datetime.time(hour, minute)


def parse_weekdays(weekday_list_text):
    '''
    Parse a list of weekdays, like `TR` for thursday, `MW` for monday and
    wednesday, returns a list of ints that correspond to those days,
    like `datetime.date.weekday()`
    '''
    WEEKDAY_ABREV_ORDER = ['M', 'T', 'W', 'R', 'F']

    for weekday_int, weekday_abrev in enumerate(WEEKDAY_ABREV_ORDER):
        if weekday_abrev in weekday_list_text:
            yield weekday_int


def get_courses(username, password):
    '''
    return a list of dicts, for each course the user is taking, that look like
    this

    {
        'credits': '    1.000',
        'weekdays': [3],
        'end_time': datetime.time(11, 10),
        'instructor': 'Simonson M',
        'location': '105 LITTLE',
        'number': '200',
        'reg_number': '10643',
        'section': 'A',
        'start_time': datetime.time(9, 55),
        'status': 'Registered',
        'subject': 'FMST',
        'title': 'Introduction to Film and Media Studies'}
    },
    ...
    '''
    session = requests.Session()
    login_to_portal(session, username, password)

    # must get IDMSESSID cookie from this url
    r = session.get('http://bannersv04.colgate.edu:10003/ssomanager/c/SSB')

    # then can get schedule
    SCHEDULE_URL = 'https://bannersv04.colgate.edu/prod/bwskfshd.P_CrseSchdDetl'
    r = session.get(SCHEDULE_URL)
    soup = bs4.BeautifulSoup(r.text)
    courses_table = soup.find('table', class_='datadisplaytable')
    # skip the first and last row, because they are not courses
    courses = courses_table.find_all('tr')[1:-1]
    for course in courses:

        fields = map(lambda tag: tag.text, course.find_all('td'))
        field_names = [
            'reg_number',
            'subject',
            'number',
            'section',
            'title',
            'credits',
            'status',
            'time, weekdays, location',
            'instructor'
        ]
        course_dict = dict(zip(field_names, fields))

        course_dict['time'], course_dict['weekdays'], course_dict['location'] = \
            course_dict['time, weekdays, location'].split(', ')
        del course_dict['time, weekdays, location']

        course_dict['start_time'], course_dict['end_time'] = \
            course_dict['time'].split('-')
        del course_dict['time']

        course_dict['start_time'] = parse_time(course_dict['start_time'])
        course_dict['end_time'] = parse_time(
            course_dict['end_time'],
            force_pm=course_dict['start_time'].hour > 12
        )

        course_dict['weekdays'] = list(parse_weekdays(course_dict['weekdays']))

        yield course_dict


def get_ics_text(username, password):
    cal = ics.Calendar()
    courses = list(get_courses(username, password))
    for date in get_school_days():
        for course in courses:
            for weekday in course['weekdays']:
                if weekday == date.weekday():
                    event = ics.Event()
                    event.name = course['title']
                    event.location = course['location']
                    if course['start_time']:
                        eastern = pytz.timezone('US/Eastern')
                        event.begin = eastern.localize(datetime.datetime.combine(date, course['start_time']))
                        event.end = eastern.localize(datetime.datetime.combine(date, course['end_time']))
                    else:
                        event.begin = date
                        event.make_all_day()
                    cal.events.append(event)
    return cal
