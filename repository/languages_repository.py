from repository.connect import languages
import toolz as t

def find_all():
    return t.pipe(
        languages.find(),
        list
    )