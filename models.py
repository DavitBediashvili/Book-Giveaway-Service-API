

class Book:
    def __init__(self, id, owner, title, author, genre, condition, location):
        self.id = id
        self.owner = owner
        self.title = title
        self.author = author
        self.genre = genre
        self.condition = condition
        self.location = location

    def __json__(self):
        return {
            "owner": self.owner,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "condition": self.condition,
            "location": self.location
        }

class Genre:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __json__(self):
        return {
            "name": self.name
        }
    
class Author:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __json__(self):
        return {
            "name": self.name
        }
    
    