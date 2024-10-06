from repository.connect import languages

if __name__ == '__main__':
    print(list(languages.find({ 'paradigms': { '$all': ['Functional', 'Object-Oriented']}}).limit(1)))