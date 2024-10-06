from pymongo.synchronous.collection import Collection
from bson import ObjectId
from returns.maybe import Maybe, Some, Nothing
from operator import itemgetter, eq
import toolz as t

def test_find_all(jokes_collection: Collection):
    results = list(jokes_collection.find())
    assert len(results) > 0
   
def test_limit_5(jokes_collection: Collection):
    results = list(jokes_collection.find().limit(5))
    assert len(results) <= 5

def test_by_id(jokes_collection: Collection):
    result = Maybe.from_optional(jokes_collection.find_one({ '_id': ObjectId('66fe8c7a1b4666209d63e0ba')}))
    assert isinstance(result, Some)

def test_by_popular_state(jokes_collection: Collection):
    results = list(jokes_collection.find({ 'popular_state': 'Georgia'}))
    assert len(results) > 0 

def test_count_documents(jokes_collection: Collection):
    result = jokes_collection.count_documents({})
    assert result > 0


def test_find_jokes_containing_word(jokes_collection: Collection):
    result = list(jokes_collection.find({ 'joke': {
        '$regex': 'why',
        '$options': 'i'
    }}))
    assert len(result) > 0

def test_find_by_word_and_not_state(jokes_collection: Collection):
    results = list(jokes_collection.find({
        'joke': { '$regex': 'why', '$options': 'i'},
        'popular_state': { '$ne': 'Georgia' }
    }))
    assert len(results) > 0

def test_update_popular_state(jokes_collection: Collection):
    id = '66ff71b119275ed533e7f96e'
    popular_state = 'Tel Aviv'
    jokes_collection.update_one({ '_id': ObjectId(id)}, { '$set': { 'popular_state': popular_state }})
    assert (Maybe.from_optional(jokes_collection.find_one({ '_id': ObjectId(id)}))
            .map(itemgetter("popular_state"))
            .map(t.partial(eq, popular_state))
            .value_or(False))

def test_delete_joke_by_id(jokes_collection: Collection):
    id = '66ff71b119275ed533e7f96e'
    jokes_collection.delete_one({ '_id': ObjectId(id)})
    assert Maybe.from_optional(jokes_collection.find_one({ '_id': ObjectId(id)})) is Nothing

def test_insert_joke(jokes_collection: Collection):
    joke = { 'joke': "this is a funny stuff", 'popular_state': 'Rishon le zion' }
    jokes_collection.insert_one(joke)
    assert Maybe.from_optional(jokes_collection.find_one({ 'joke': joke['joke'] })) is not Nothing
    
def test_find_first_joke_sorted(jokes_collection: Collection):
    assert (Maybe.from_optional(jokes_collection.find_one(sort=[('joke', 1)]))
            .map(itemgetter('joke'))
            .map(lambda j: j.startswith('A'))
            .value_or(False))
    
def test_find_jokes_multiple_states(jokes_collection: Collection):
    popular_states = ['Georgia', 'Michigan']
    res = list(jokes_collection.find({ 'popular_state': { '$in': popular_states }}))
    assert all(j['popular_state'] in popular_states for j in res) 

def test_update_replace(jokes_collection: Collection):
    jokes_collection.update_many(
        {'joke': {'$regex': 'why', '$options': 'i'}}, 
        [{'$set': {'joke': {'$replaceAll': {
            'input': '$joke', 
            'find': 'Why', 
            'replacement': 'Cause'
            }}}
         }])
    assert all('Why' not in j['joke'] for j in jokes_collection.find())

def test_update_many_states(jokes_collection: Collection):
    popular_state = 'Haifa'
    search = { 'joke': { '$regex': 'why', '$options': 'i' }}
    jokes_collection.update_many(search,[{ '$set': { 'popular_state': popular_state }}])
    jokes_with_why = jokes_collection.find(search)
    assert all(j['popular_state'] == popular_state for j in jokes_with_why)


def test_find_jokes_by_state_michigan(jokes_collection: Collection):
    popular_state_start = 'Mic'
    res = list(jokes_collection.find({ 'popular_state':  { 
        '$regex': f'^{popular_state_start}', '$options': 'i' 
    }}))
    assert all(j['popular_state'].startswith(popular_state_start) for j in res) 

def test_find_jokes_startswith(jokes_collection: Collection):
    startswith = "Why"
    res = list(jokes_collection.find({ 'joke': { '$regex': f'^{startswith}', '$options': 'i' }}))
    assert all(j['joke'].lower().startswith(startswith.lower()) for j in res)

def test_find_jokes_endswith(jokes_collection: Collection):
    endswith = 'code.'
    res = list(jokes_collection.find({ 'joke': { '$regex': f'{endswith}$', '$options': 'i' }}))
    assert all(j['joke'].endswith(endswith) for j in res)

def test_find_joke_by_two_words(jokes_collection: Collection):
    word1 = 'why'
    word2 = 'code'
    res = list(jokes_collection.find({  '$and': [
            { 'joke': {'$regex': word1, '$options': 'i'} },
            { 'joke': {'$regex': word2, '$options': 'i'} }
        ]
    }))
    assert all(
        all(word.lower() in joke['joke'].lower() for word in [word1, word2]) 
        for joke in res
    )
    
def test_find_jokes_by_id(jokes_collection: Collection):
    id = '66ff71b119275ed533e7f96e'
    res = Maybe.from_optional(jokes_collection.find_one({ '_id': ObjectId(id)}))
    c = jokes_collection.count_documents({})
    print(c)
    assert True 
    
def test_find_long_jokes(jokes_collection: Collection):
    min_words = 15
    res = list(jokes_collection.find({
        '$expr': {
            '$gt': [{'$size': {'$split': ['$joke', ' ']}}, min_words]
        }
    }))
    assert all(len(j['joke'].split()) > min_words for j in res)

def test_find_jokes_by_word_aggregate(jokes_collection: Collection):
    word = 'why'
    res = list(jokes_collection.aggregate([
        { '$match': { 'joke': { '$regex': word, '$options': 'i' }}},
        { '$project': { '_id': 0, 'joke': 1 }},
        { '$sort': { 'joke': 1 }},
        { '$limit': 1 }
    ]))
    assert all(word in joke['joke'].lower() for joke in res)

def test_jokes_by_state(jokes_collection: Collection):
    res = list(jokes_collection.aggregate([
        { '$group': {'_id': '$popular_state' , 'joke_count': { '$sum': 1 }}}
    ]))
    assert all('_id' in joke and 'joke_count' in joke for joke in res)

def test_jokes_by_word_count(jokes_collection: Collection):
    result = list(jokes_collection.aggregate([
        { '$project': {'_id': 0, 'joke': 1, 'word_count': { '$size': { '$split': ['$joke', ' '] }} } },
        {'$group': {'_id': '$word_count', 'jokes': {'$push': '$joke'}}}
    ]))
    assert all(joke['_id'] == len(joke['jokes'][0].split()) for joke in result)