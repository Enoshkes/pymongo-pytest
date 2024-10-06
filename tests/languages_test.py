from pymongo.synchronous.collection import Collection

def test_find_all(languages_collection: Collection):
    results = list(languages_collection.find())
    assert len(results) > 0

def test_find_by_paradigm_exclude_java(languages_collection: Collection):
    results = list(languages_collection.find({
        'paradigms': { '$regex': 'functional', '$options': 'i'},
        'language': { '$ne': 'Java' }
    }))
    assert len(results) > 0
    assert all('Java' not in languae['paradigms'] for languae in results)

def test_find_oop_and_fp(languages_collection: Collection):
    paradigms = ['Functional', 'Object-Oriented']
    results = list(languages_collection.find({
        'paradigms': { '$all': paradigms }
    }))
    assert len(results) > 0
    assert all(all(p in language['paradigms'] for p in paradigms) for language in results)