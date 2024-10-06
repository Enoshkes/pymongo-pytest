from repository.connect import articles
from typing import Dict, List
import toolz as t

def find_all() -> List[Dict[str, str]]:
    return t.pipe(
        articles.find(),
        list
    ) 