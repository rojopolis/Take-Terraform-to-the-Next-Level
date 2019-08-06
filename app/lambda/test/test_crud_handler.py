''' Tests of crud handler's endpoints '''
from os import path
import boto3
import pytest
from hashlib import md5
from moto import mock_dynamodb2
from functions.crud_handler import app
from populate_ddb import read_to_dicts, write_to_ddb

MOCK_TABLE_ID = 'MOCK_TABLE'

@pytest.fixture(scope='session')
def monkeypatch_session():
    from _pytest.monkeypatch import MonkeyPatch
    m = MonkeyPatch()
    m.setenv('AGENCY_TABLE_ID', MOCK_TABLE_ID)
    yield m
    m.undo()

@pytest.fixture
def event():
    return { 'httpMethod': 'GET',
             'path': 'my90/api/topics',
             'queryStringParameters': {},
             'pathParameters': { 'aId': 'AID-4j9etjej' } }

@pytest.fixture
def context():
    return None

def test_entry_point_not_get(event, context):
    event['httpMethod'] = 'PUT',
    with pytest.raises(NotImplementedError):
        app.entrypoint(event, context)


def test_entry_point_bad_route(event, context):
    event['path'] = 'my90/api/notimplemented'
    with pytest.raises(NotImplementedError):
        app.entrypoint(event, context)


def test_entrypoint_no_aid(event, context):
    event['pathParameters'] = {}
    with pytest.raises(TypeError):
        app.entrypoint(event, context)

@mock_dynamodb2
def test_agency_bad_key(monkeypatch_session):
    '''Test non-agency key'''
    _setup_ddb()
    # Agency key must start with 'AID_'
    bad_key = "LO_DOWN_FA"
    with pytest.raises(TypeError):
        app.agency(bad_key)

@mock_dynamodb2
def test_agency_missing_agency(monkeypatch_session):
    '''Test key for non-existant agency'''
    _setup_ddb()
    key = "AID-NO-AGENCY-LIKE-THIS"
    response = app.agency(key)
    assert isinstance(response, dict)
    assert len(response['Items']) == 0

@mock_dynamodb2
def test_agency_valid_response(monkeypatch_session):
    _setup_ddb()

    aid = 'AID-LI-SPD-630'
    response = app.agency(aid)

    expected_keys = {'My90EncounterScore', 'CityRacePercent', 
                     'CityGenderPercent', 'Partition', 'My90GeneralScore', 
                     'CityPopulation', 'Sort', 'LSI', 'ZoneofInterest', 
                     'CityAgePercent'}
    assert isinstance(response, dict)
    assert len(response['Items']) == 1
    assert set(response['Items'][0].keys()) == expected_keys
    assert response['Items'][0]['Partition'] == aid


@mock_dynamodb2
def test_questions_valid(monkeypatch_session):
    _setup_ddb()

    aid = 'AID-MO-SPD-245'
    response = app.questions(aid)
    assert len(response['Items']) == 18
    expected_keys = {'QuestionChoicesId', 'Sort', 'Category', 'Partition', 'Text'}
    assert all([set(x.keys()).issubset(expected_keys) for x in response['Items']])
    assert all([x['Partition'] == aid for x in response['Items']])
    assert all([x['Sort'].startswith('QID-') for x in response['Items']])


@mock_dynamodb2
def test_questions_paging(monkeypatch_session):
    _setup_ddb()

    aid = 'AID-MO-SPD-245'
    response = app.questions(aid, limit=1)
    assert len(response['Items']) == 1
    assert 'LastEvaluatedKey' in response
    response = app.questions(aid, exclusiveStartKey=str(response['LastEvaluatedKey']))
    assert len(response['Items']) == 17


@mock_dynamodb2
def test_questions_bad_aid(monkeypatch_session):
    _setup_ddb()
    # Agency key must start with 'AID_'
    bad_key = "LO_DOWN_FA"
    with pytest.raises(TypeError):
        app.agency(bad_key)


@mock_dynamodb2
def test_questions_aid_with_no_questions(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-LI-SPD-630'
    response = app.responses(aid)
    assert isinstance(response, dict)
    assert len(response['Items']) == 0


@mock_dynamodb2
def test_responses_valid(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'

    response = app.responses(aid)
    assert len(response['Items']) == 461
    expected_keys = {'Choice', 'LSI', 'Date', 'Sort', 'Partition', 'Topic', 
                     'Gender', 'Longitude', 'RespondentId', 'Age', 'Latitude', 
                     'Origin', 'Race', 'IncidentCode', 'IncidentId', 'Sentiment',
                     'my90EncounterScore', 'Text', 'my90GeneralScore', 'QuestionChoicesId'}
    assert all([set(x.keys()).issubset(expected_keys) for x in response['Items']])
    assert all([x['Partition'] == aid for x in response['Items']])
    assert all([x['Sort'].startswith('RID-') for x in response['Items']])


@mock_dynamodb2
def test_responses_paging(monkeypatch_session):
    _setup_ddb()

    aid = 'AID-MO-SPD-245'
    response = app.responses(aid, limit=1)
    assert len(response['Items']) == 1
    assert 'LastEvaluatedKey' in response
    response = app.responses(aid, exclusiveStartKey=str(response['LastEvaluatedKey']))
    assert len(response['Items']) == 460


@mock_dynamodb2
def test_responses_bad_aid(monkeypatch_session):
    _setup_ddb()
    # Agency key must start with 'AID_'
    bad_key = "LO_DOWN_FA"
    with pytest.raises(TypeError):
        app.agency(bad_key)


@mock_dynamodb2
def test_responses_aid_no_responses(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-LI-SPD-630'
    response = app.responses(aid)
    assert isinstance(response, dict)
    assert len(response['Items']) == 0


@mock_dynamodb2
def test_responses_startDate(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    startDate = 1538357443
    response = app.responses(aid, startDate=startDate)
    assert len(response['Items']) == 461
    assert all([x['Date'] >= startDate for x in response['Items']])


@mock_dynamodb2
def test_responses_endDate(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    endDate = 1539358443
    response = app.responses(aid, endDate=endDate)
    assert len(response['Items']) == 185
    assert all([x['Date'] <= endDate for x in response['Items']])


@mock_dynamodb2
def test_responses_startDate_endDate(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    startDate = 1538357443
    endDate = 1539358443
    response = app.responses(aid, startDate=startDate, endDate=endDate)
    assert len(response['Items']) == 185
    assert all([x['Date'] >= startDate for x in response['Items']])
    assert all([x['Date'] <= endDate for x in response['Items']])


@mock_dynamodb2
def test_responses_age(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    ages = [ 0, 2, 3]

    response = app.responses(aid, age=ages)
    assert len(response['Items']) == 235
    assert all([x['Age'] in ages for x in response['Items']])


@mock_dynamodb2
def test_responses_gender(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    genders = [ 0, 2, 3]

    response = app.responses(aid, gender=genders)
    assert len(response['Items']) == 333
    assert all([x['Gender'] in genders for x in response['Items']])


@mock_dynamodb2
def test_responses_race(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    races = [ 0, 2, 3]

    response = app.responses(aid, race=races)
    assert len(response['Items']) == 205
    assert all([x['Race'] in races for x in response['Items']])


@mock_dynamodb2
def test_responses_sentiment(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    sentiments = [ 0, 2, 3]

    response = app.responses(aid, sentiment=sentiments)
    assert len(response['Items']) == 289
    assert all([x['Sentiment'] in sentiments for x in response['Items']])


@mock_dynamodb2
def test_responses_origin(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    origins = [ 0, 2, 3]

    response = app.responses(aid, origin=origins)
    assert len(response['Items']) == 316
    assert all([x['Origin'] in origins for x in response['Items']])


@mock_dynamodb2
def test_responses_topic(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    topic = 2

    response = app.responses(aid, topic=topic)
    assert len(response['Items']) == 157
    assert all([x['Topic'] == topic for x in response['Items']])


@mock_dynamodb2
def test_responses_geo(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    # [bottom left coordinates, upper right coordinates] 
    geo = "41.150740,-110.702522,44.667432,-104.200369"
    response = app.responses(aid, geo=geo)
    assert len(response['Items']) == 2
    assert all([41 < float(x['Latitude']) < 44.7 for x in response['Items']])
    assert all([-110.8 < float(x['Longitude']) < -104 for x in response['Items']])


@mock_dynamodb2
def test_responses_geo_wide_search(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    # [bottom left coordinates, upper right coordinates] 
    geo = '27.449790329784214,-142.55859375000003,53.592504809039376,-32.69531250000001'
    response = app.responses(aid, geo=geo)
    assert len(response['Items']) == 461
    assert all([ 27 < x['Latitude'] < 54 for x in response['Items']])
    assert all([-143 < x['Longitude'] < -33 for x in response['Items']])


@mock_dynamodb2
def test_responsesMetadata(monkeypatch_session):
    _setup_ddb()
    def _total_count(data):
        return sum([x['count'] for x in data])

    aid = 'AID-MO-SPD-245'
    response = app.responsesMetadata(aid)
    expected_keys = {'sentiment', 'age','gender','race','dayCount'}
    items = response['Items']
    assert expected_keys == set(items.keys())
    assert _total_count(items['age']) == _total_count(items['gender']) == _total_count(items['race']) == _total_count(items['dayCount'])
    

@mock_dynamodb2
def test_questionResponsesMetadata(monkeypatch_session):
    _setup_ddb()
    aid = 'AID-MO-SPD-245'
    qid = 'QID-1012'
    response = app.questionResponsesMetadata(aid, qid)
    expected_keys = {'sentiment','age','gender','race','dayCount'}
    items = response['Items']
    assert expected_keys == set(items.keys())


def test_count_and_mean():
    items = [ {'Date': 1538982000, 'Sentiment': 0, 'Gender': 0, 'Age': 0, 'Race': 0, 'my90EncounterScore': 10, 'my90GeneralScore':  5},
              {'Date': 1538809200, 'Sentiment': 1, 'Gender': 1, 'Age': 1, 'Race': 1, 'my90EncounterScore': 20, 'my90GeneralScore': 10},
              {'Date': 1539846000, 'Sentiment': 2, 'Gender': 2, 'Age': 2, 'Race': 2, 'my90EncounterScore': 30, 'my90GeneralScore': 20},
              {'Date': 1538636400, 'Sentiment': 0, 'Gender': 3, 'Age': 3, 'Race': 3, 'my90EncounterScore': 40, 'my90GeneralScore': 30},
              {'Date': 1538722800, 'Sentiment': 1, 'Gender': 0, 'Age': 4, 'Race': 4, 'my90EncounterScore': 50, 'my90GeneralScore': 40},
              {'Date': 1539068400, 'Sentiment': 0, 'Gender': 1, 'Age': 5, 'Race': 5, 'my90EncounterScore': 60, 'my90GeneralScore': 50},
              {'Date': 1538722800, 'Sentiment': 1, 'Gender': 0, 'Age': 0, 'Race': 6, 'my90EncounterScore': 70, 'my90GeneralScore': 60},
              {'Date': 1538982000, 'Sentiment': 2, 'Gender': 1, 'Age': 1, 'Race': 0, 'my90EncounterScore': 80, 'my90GeneralScore': 70},
              {'Date': 1538809200, 'Sentiment': 0, 'Gender': 0, 'Age': 2, 'Race': 1, 'my90EncounterScore': 90, 'my90GeneralScore': 80},
              {'Date': 1539846000, 'Sentiment': 1, 'Gender': 2, 'Age': 3, 'Race': 2, 'my90EncounterScore': 95, 'my90GeneralScore': 90},
              {'Date': 1538636400, 'Sentiment': 2, 'Gender': 0, 'Age': 4, 'Race': 3, 'my90EncounterScore':  5, 'my90GeneralScore': 95} ]
    
    expected_result = {'age': [{'count': 2, 'my90EncounterScoreAvg': 40, 'my90GeneralScoreAvg': 32.5},
                               {'count': 2, 'my90EncounterScoreAvg': 50, 'my90GeneralScoreAvg': 40},
                               {'count': 2, 'my90EncounterScoreAvg': 60, 'my90GeneralScoreAvg': 50},
                               {'count': 2, 'my90EncounterScoreAvg': 67.5, 'my90GeneralScoreAvg': 60},
                               {'count': 2,
                                'my90EncounterScoreAvg': 27.5,
                                'my90GeneralScoreAvg': 67.5},
                               {'count': 1, 'my90EncounterScoreAvg': 60, 'my90GeneralScoreAvg': 50}],
                      'dayCount': [{'count': 2,
                                    'my90EncounterScoreAvg': 22.5,
                                    'my90GeneralScoreAvg': 62.5},
                                   {'count': 2,
                                    'my90EncounterScoreAvg': 60,
                                    'my90GeneralScoreAvg': 50},
                                   {'count': 2,
                                    'my90EncounterScoreAvg': 55,
                                    'my90GeneralScoreAvg': 45},
                                   {'count': 2,
                                    'my90EncounterScoreAvg': 45,
                                    'my90GeneralScoreAvg': 37.5},
                                   {'count': 1,
                                    'my90EncounterScoreAvg': 60,
                                    'my90GeneralScoreAvg': 50},
                                   {'count': 2,
                                    'my90EncounterScoreAvg': 62.5,
                                    'my90GeneralScoreAvg': 55}],
                       'sentiment': [{'count': 4, 'my90EncounterScoreAvg': 50, 'my90GeneralScoreAvg': 41.25}, 
                                     {'count': 4, 'my90EncounterScoreAvg': 58.75, 'my90GeneralScoreAvg': 50}, 
                                     {'count': 3, 'my90EncounterScoreAvg': 38.333333333333336, 'my90GeneralScoreAvg': 61.666666666666664}],
                      'gender': [{'count': 5,
                                  'my90EncounterScoreAvg': 45,
                                  'my90GeneralScoreAvg': 56},
                                 {'count': 3,
                                  'my90EncounterScoreAvg': 53.333333333333336,
                                  'my90GeneralScoreAvg': 43.333333333333336},
                                 {'count': 2,
                                  'my90EncounterScoreAvg': 62.5,
                                  'my90GeneralScoreAvg': 55},
                                 {'count': 1,
                                  'my90EncounterScoreAvg': 40,
                                  'my90GeneralScoreAvg': 30}],
                      'race': [{'count': 2,
                                'my90EncounterScoreAvg': 45,
                                'my90GeneralScoreAvg': 37.5},
                               {'count': 2, 'my90EncounterScoreAvg': 55, 'my90GeneralScoreAvg': 45},
                               {'count': 2,
                                'my90EncounterScoreAvg': 62.5,
                                'my90GeneralScoreAvg': 55},
                               {'count': 2,
                                'my90EncounterScoreAvg': 22.5,
                                'my90GeneralScoreAvg': 62.5},
                               {'count': 1, 'my90EncounterScoreAvg': 50, 'my90GeneralScoreAvg': 40},
                               {'count': 1, 'my90EncounterScoreAvg': 60, 'my90GeneralScoreAvg': 50},
                               {'count': 1, 'my90EncounterScoreAvg': 70, 'my90GeneralScoreAvg': 60}]}


    result = app.count_and_mean(items)
    assert result == expected_result


def test_count_and_mean_missing_values():
    items = [{'Date': 1539846000, 'Sentiment':3, 'Gender': 2, 'Age': 2, 'Race': 2, 'my90EncounterScore': 30, 'my90GeneralScore': 20}]
    expected_result = {'age': [{'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 1, 'my90EncounterScoreAvg': 30, 'my90GeneralScoreAvg': 20},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0}],
                       'race':[{'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 1, 'my90EncounterScoreAvg': 30, 'my90GeneralScoreAvg': 20},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0}],
                       'sentiment': [{'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0}, 
                                     {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0}, 
                                     {'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0}],
                       'gender':[{'count': 0, 'my90EncounterScoreAvg': 0, 'my90GeneralScoreAvg': 0},
                               {'count': 0, 'my90EncounterScoreAvg': 0,   'my90GeneralScoreAvg': 0},
                               {'count': 1, 'my90EncounterScoreAvg': 30,  'my90GeneralScoreAvg': 20},
                               {'count': 0, 'my90EncounterScoreAvg': 0,   'my90GeneralScoreAvg': 0}],
                       'dayCount':[{'count':1, 'my90EncounterScoreAvg': 30, 'my90GeneralScoreAvg': 20}]}
    result = app.count_and_mean(items)
    assert result == expected_result
    
@mock_dynamodb2
def test_count_by_scale(monkeypatch_session):
    _setup_ddb()
    items = [ {'Partition': 'AID-MO-SPD-245', 'Sentiment': 0, 'Date': 1538982000, 'Gender': 0, 'Age': 0, 'Race': 0, 'Choice': 0, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 1, 'Date': 1538809200, 'Gender': 1, 'Age': 1, 'Race': 1, 'Choice': 2, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 2, 'Date': 1539846000, 'Gender': 2, 'Age': 2, 'Race': 2, 'Choice': 3, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 0, 'Date': 1538636400, 'Gender': 3, 'Age': 3, 'Race': 3, 'Choice': 4, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 1, 'Date': 1538722800, 'Gender': 0, 'Age': 4, 'Race': 4, 'Choice': 0, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 2, 'Date': 1539068400, 'Gender': 1, 'Age': 5, 'Race': 5, 'Choice': 1, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 0, 'Date': 1538722800, 'Gender': 0, 'Age': 0, 'Race': 6, 'Choice': 2, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 1, 'Date': 1538982000, 'Gender': 1, 'Age': 1, 'Race': 0, 'Choice': 3, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 2, 'Date': 1538809200, 'Gender': 0, 'Age': 2, 'Race': 1, 'Choice': 4, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 0, 'Date': 1539846000, 'Gender': 2, 'Age': 3, 'Race': 2, 'Choice': 0, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'},
              {'Partition': 'AID-MO-SPD-245', 'Sentiment': 1, 'Date': 1538636400, 'Gender': 0, 'Age': 4, 'Race': 3, 'Choice': 1, 'QuestionChoicesId': 'QCID-260c796d792e02483619349ba9dee233'}]

    expected_result = {'age': [[1, 0, 1, 0, 0],
                               [0, 0, 1, 1, 0],
                               [0, 0, 0, 1, 1],
                               [1, 0, 0, 0, 1],
                               [1, 1, 0, 0, 0],
                               [0, 1, 0, 0, 0]],
                       'race': [[1, 0, 0, 1, 0],
                                [0, 0, 1, 0, 1],
                                [1, 0, 0, 1, 0],
                                [0, 1, 0, 0, 1],
                                [1, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0],
                                [0, 0, 1, 0, 0]],
                       'gender': [[2, 1, 1, 0, 1],
                                  [0, 1, 1, 1, 0],
                                  [1, 0, 0, 1, 0],
                                  [0, 0, 0, 0, 1]],
                       'sentiment': [[2, 0, 1, 0, 1], 
                                     [1, 1, 1, 1, 0], 
                                     [0, 1, 0, 1, 1]],
                       'dayCount': [[0, 1, 0, 0, 1],
                                    [1, 0, 1, 0, 0],
                                    [0, 0, 1, 0, 1],
                                    [1, 0, 0, 1, 0],
                                    [0, 1, 0, 0, 0],
                                    [1, 0, 0, 1, 0]]}
    result = app.count_by_scale(items)
    assert result == expected_result


@mock_dynamodb2
def test_questionChoices_good(monkeypatch_session):
    '''Test getting question choices entry which exists'''
    _setup_ddb()
    aid = 'AID-LI-SPD-630'
    choices = ('choice-1','choice-2','choice-3','choice-4')
    h = md5()
    h.update(str(choices).encode())
    qcid = f"QCID-{h.hexdigest()}"
    response = app.questionChoices(aid, qcid)
    assert response['Items'][qcid] == choices


@mock_dynamodb2
def test_questionChoices_paging(monkeypatch_session):
    _setup_ddb()

    aid = 'AID-MO-SPD-245'
    response = app.questionChoices(aid, limit=1)
    assert len(response['Items']) == 1
    assert 'LastEvaluatedKey' in response
    response = app.questionChoices(aid, 
                                   exclusiveStartKey=str(response['LastEvaluatedKey']))
    assert len(response['Items']) == 10


@mock_dynamodb2
def test_questionChoices_missing(monkeypatch_session):
    '''Test getting question choices entry which does not exist'''
    _setup_ddb()
    aid = 'AID-LI-SPD-630'
    choices = ('no','choices','like','this')
    h = md5()
    h.update(str(choices).encode())
    qcid = f"QCID-{h.hexdigest()}"
    response = app.questionChoices(aid, qcid)
    assert response['Items'] == {}


@mock_dynamodb2
def test_questionChoices_all(monkeypatch_session):
    '''Test getting all question choices'''
    _setup_ddb()
    aid = 'AID-LI-SPD-630'
    response = app.questionChoices(aid)
    items = response['Items']
    assert len(items) == 2
    assert all([x.startswith('QCID') for x in items.keys()])


def test_field_count_by_scale():
    field_name = 'group_field'
    keys = ['key1', 'key2']
    group_field = 'group field'
    indices = [0,1]
    data = [ { field_name: 0, group_field: 0},
             { field_name: 1, group_field: 1}]

    expected_output = [[1, 0], [0,1]]
    result = app.field_count_by_scale(field_name, data, indices, group_field=group_field, keys=keys)
    assert result == expected_output


def _setup_ddb():
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    dynamodb.create_table(TableName=MOCK_TABLE_ID,
                          KeySchema=[{'AttributeName':'Partition','KeyType':'HASH'}, 
                                     {'AttributeName':'Sort','KeyType':'RANGE'}],
                          AttributeDefinitions=[{'AttributeName':'Partition','AttributeType':'S'},
                                                {'AttributeName':'Sort','AttributeType':'S'}],
                          ProvisionedThroughput={'ReadCapacityUnits':5,'WriteCapacityUnits':5})
    data = read_to_dicts('DDB-surveys-questions-responses.csv')
    write_to_ddb(data)
    data = read_to_dicts('DDB-agencies.csv')
    write_to_ddb(data)
