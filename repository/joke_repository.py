from repository.connect import jokes
from typing import List, Dict
from returns.maybe import Maybe
from returns.result import Result, Success, Failure
import toolz as t

def first_five() -> List[Dict[str, str]]:
    return t.pipe(
        jokes.find().limit(5),
        list
    )

def find_one_including(phrase: str) -> Maybe[Dict[str, str]]:
    return t.pipe(
        jokes.find_one({ 'joke': { '$regex': phrase, '$options': 'i' }}),
        Maybe.from_optional    
    )

def find_all() -> List[Dict[str, str]]:
    return t.pipe(
        jokes.find(),
        list
    )