from pymongo.synchronous.collection import Collection
from returns.maybe import Maybe, Nothing, Some
from datetime import datetime

def test_title_containing_phrase(articles_collection: Collection):
    word = 'the'
    res = list(articles_collection.find({ 'title': {
        '$regex': word,
        '$options': 'i'
    }}))
    assert all(word in article['title'].lower() for article in res)

def test_content_by_word_not_author(articles_collection: Collection):
    results = list(articles_collection.find({
        'content': { '$regex': 'the', '$options': 'i'},
        'author.first_name': { '$ne': 'John' }
    }))
    assert len(results) > 0
    assert all(a['author']['first_name'] != 'John' for a in results)

def test_find_most_recent_article(articles_collection: Collection):
    maybe_article = Maybe.from_optional(articles_collection.find_one(sort=[('published_date', -1)]))
    assert isinstance(maybe_article, Some)
    
def test_find_article_in_range(articles_collection: Collection):
    start_date = datetime(2023, 10, 1).strftime("%Y-%m-%d")
    end_date = datetime(2023, 11, 5).strftime("%Y-%m-%d")

    res = list(articles_collection.find({ 'published_date': {
        '$gte': start_date, 
        '$lte': end_date 
    }}))
    assert len(res) > 0

    
def test_find_more_than_paragraph(articles_collection: Collection):
    res = list(articles_collection.find({ '$expr': {
        '$gt': [{'$size': '$content'}, 1] 
    } }))
    assert all(len(a['content']) > 1 for a in res)

def test_articles_by_year_group_by_author(articles_collection: Collection):
    articles = articles_collection.aggregate([ 
        {'$match': {'published_date': {'$regex': f'2023-10'}}},
        {'$group': {'_id': '$author.last_name', 'articles': {'$push': '$title'}}} 
    ])
    assert len(articles) > 0

