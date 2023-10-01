from flask import Flask, jsonify, request, session
import sqlite3
import bcrypt
import jwt
import datetime
from flask_login import UserMixin
from models import Genre, Book, Author

app = Flask(__name__)
app.secret_key = "scooby-doo"
secret_key = "scooby-doo"


connect = sqlite3.connect('bookgive.db', check_same_thread=False)
con = connect.cursor()


class User(UserMixin):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

# user table(user with id 1 is considered admin)
con.execute('''CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)''')

# books table
con.execute('''CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    condition TEXT NOT NULL CHECK (condition IN ('new', 'good', 'fair', 'poor')),
    location TEXT NOT NULL
)''')

# genres table
con.execute('''CREATE TABLE IF NOT EXISTS genres(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)''')  

# authors table
con.execute('''CREATE TABLE IF NOT EXISTS authors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)''')  

books_table_columns = {'owner', 'title', 'author', 'genre', 'condition', 'location'}
users_table_columns = {'email', 'password'}


# JWT token generator
def generate_jwt_token(user, id):
    payload = {
    "sub": id,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=160)
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')

    return token    





@app.route('/register', methods=['POST'])
def register():
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']

    # Check if email  already exists.
    con.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = con.fetchone()
    if user is not None:
        return jsonify({'message': 'Email is already in use'}), 400
    
    # Check if name  already exists.
    con.execute('SELECT * FROM users WHERE name = ?', (name,))
    user = con.fetchone()
    if user is not None:
        return jsonify({'message': 'Email is already in use'}), 400
    
    # encode and hash password
    encoded_password = password.encode()
    password_hash = bcrypt.hashpw(encoded_password, bcrypt.gensalt())

    # add new user to users table
    con.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password_hash))
    connect.commit()

    # get id
    # last_inserted_id = con.lastrowid

    return jsonify({'message': 'User registered successfully.'})


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    # Check if user is in the database
    con.execute('SELECT * FROM users WHERE email = ?', (email,))
    user_data = con.fetchone()
    if user_data is None:
        return jsonify({'message': 'Email does not exist.'}), 401

    decode_byte = user_data[3].decode('utf-8')
    stored_password = decode_byte.encode()
    name = user_data[1]
    email = user_data[2]
    user_id = user_data[0]

    if not bcrypt.checkpw(password.encode(), stored_password):
        return jsonify({'message': 'Incorrect password.'}), 401

    # Create a user object for Flask-Login
    user = User(user_id, name, email)

    # Generate a JWT token
    token = generate_jwt_token(user, user_id)

    return jsonify({"token": token, "name": name})





# full book list
@app.route('/books', methods=['GET'])
def get_full_list_books():
    con.execute('SELECT * FROM books')
    books = con.fetchall()
    return jsonify([Book(*book).__json__() for book in books])

# sorted book list, user can choose if it will be asc or desc
@app.route('/books/sorted_by/<string:sort_by>/<string:asc_desc>', methods=['GET'])
def sorted_books(sort_by, asc_desc):
    # Check if the sort_by parameter is correct
    valid_sort_by_fields = ['owner', 'title', 'author', 'genre', 'condition', 'location']
    if sort_by not in valid_sort_by_fields:
        return jsonify({'message': 'Invalid sort_by field: {}'.format(sort_by)}), 400

    # Check if the asc_desc parameter is correct
    valid_asc_desc_orders = ['asc', 'desc']
    if asc_desc not in valid_asc_desc_orders:
        return jsonify({'message': 'Invalid asc_desc order: {}'.format(asc_desc)}), 400

    # sort condition in non-alphabetical way
    if sort_by == 'condition' and asc_desc == 'desc':
        con.execute('SELECT * FROM books ORDER BY CASE   WHEN condition = \'new\' THEN 1     WHEN condition = \'good\' THEN 2     WHEN condition = \'fair\' THEN 3     ELSE 4 END')
    elif sort_by == 'condition' and asc_desc == 'asc':
        con.execute('SELECT * FROM books ORDER BY CASE   WHEN condition = \'poor\' THEN 1     WHEN condition = \'fair\' THEN 2     WHEN condition = \'good\' THEN 3     ELSE 4 END')
    else:
        con.execute('SELECT * FROM books ORDER BY {} {}'.format(sort_by, asc_desc))

    books = con.fetchall()
    return jsonify([Book(*book).__json__() for book in books])

# get books with specific genre
@app.route('/books/genre/<string:genre>', methods=['GET'])
def get_by_genre(genre):
  con.execute('SELECT * FROM books WHERE genre = ?', (genre,))
  books = con.fetchall()
  if books is None:
        return jsonify({'message': 'Genre does not exist: {}'.format(genre)}), 400
  return jsonify([Book(*book).__json__() for book in books])


# get book with specific id
@app.route('/books/<int:id>', methods=['GET'])
def get_by_id(id):
    con.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = con.fetchone()
    if book is None:
        return jsonify({'message': 'There is no book with that ID'}), 400
    return jsonify(Book(*book).__json__())

# add your book
@app.route('/books', methods=['POST'])
def create_new_book():
    owner = request.json['owner']
    title = request.json['title']
    author = request.json['author'].lower()
    genre = request.json['genre']
    condition = request.json['condition']
    location = request.json['location']

    #check if book condition is correct
    if condition not in ['new', 'good', 'fair', 'poor']:
        return jsonify({'message': 'Invalid condition, condition can be one of these: new, good, fair, poor'}), 400
    
    #check if this genre is in genres table
    # con.execute('SELECT * FROM genres WHERE name = ?', (genre,))
    # genr = con.fetchone()
    # if genr is None:
    #     return jsonify({'message': 'there is no such genre'}), 400
    
    #check if this author exists
    con.execute('SELECT * FROM authors WHERE name = ?', (author,))
    autho = con.fetchone()
    if autho is None:
        con.execute('INSERT INTO authors (name) VALUES (?)', (author,))
        connect.commit()

    con.execute('INSERT INTO books (owner, title, author, genre, condition, location) VALUES (?, ?, ?, ?, ?, ?)', (owner, title, author, genre, condition, location))
    connect.commit()

    
    return jsonify({'message': 'Book was added successfully'})

# change book info
@app.route('/books/<int:id>', methods=['POST'])

def update_book_info(id):
    book_data = request.json

    # check if there is book with that id
    con.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = con.fetchone()
    if book is None:
        return jsonify({'message': 'There is no book with that ID'}), 400


    # dictionary in which we will store fields and values that will be updated
    book_update_data = {}

    # filling dictionary
    for field, value in book_data.items():
        book_update_data[field] = value

    # list with field names(which should be updated)
    update_fields = list(book_update_data.keys())

    sql_update_statement = 'UPDATE books SET {} WHERE id = ?'.format(
        ', '.join(['{} = ?'.format(field) for field in update_fields])
    )

    for field in book_update_data.keys():
        if field not in books_table_columns:
            return jsonify({'message': 'Invalid book update fields'}), 400
        
    #check if book condition is correct
    if book_data.get('condition') and book_data.get('condition') not in ['new', 'good', 'fair', 'poor']:
        return jsonify({'message': 'Invalid condition, condition can be one of these: new, good, fair, poor'}), 400
    
    if book_data.get('genre'):
        con.execute('SELECT * FROM genres WHERE name = ?', (book_data.get('genre'),))
        genr = con.fetchone()
        if genr is None:
            return jsonify({'message': 'there is no such genre'}), 400

    con.execute(sql_update_statement, (*book_update_data.values(), id))
    connect.commit()

    return jsonify({'message': 'Book info was updated successfully'})

# Delete book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    #check if there is book with that id
    con.execute('SELECT * FROM books WHERE id = ?', (id,))
    book = con.fetchone()
    if book is None:
        return jsonify({'message': 'There is no book with that ID'}), 400


    con.execute('DELETE FROM books WHERE id = ?', (id,))
    connect.commit()
    return jsonify({'message': 'Book was deleted successfully'})


# get all genres
@app.route('/genres', methods=['GET'])
def get_all_genres():
    con.execute('SELECT * FROM genres')
    genres = con.fetchall()
    return jsonify([Genre(*genre).__json__() for genre in genres])

# get genre with specific id
@app.route('/genres/<int:id>', methods=['GET'])
def get_genre_id(id):
    con.execute('SELECT * FROM genres WHERE id = ?', (id,))
    genre = con.fetchone()
    if genre is None:
        return jsonify({'message': 'There is no genre with that ID'}), 400
    return jsonify(Genre(*genre).__json__())

# add new genre
@app.route('/genres', methods=['POST'])
def create_new_genre():
    name = request.json['name']
    
    con.execute('INSERT INTO genres (name) VALUES (?)', (name,))
    connect.commit()
    return jsonify({'message': 'Genre was created successfully'})

# change genre info
@app.route('/genres/<int:id>', methods=['PUT'])
def update_genre_info(id):
    name = request.json['name']

    #check if there is genre with that id
    con.execute('SELECT * FROM genres WHERE id = ?', (id,))
    genre = con.fetchone()
    if genre is None:
        return jsonify({'message': 'There is no genre with that ID'}), 400
    
    con.execute('UPDATE genres SET name = ? WHERE id = ?', (name, id))
    connect.commit()
    return jsonify({'message': 'genre info was updated successfully'})

# Delete genre
@app.route('/genres/<int:id>', methods=['DELETE'])
def delete_genre(id):
    #check if there is genre with that id
    con.execute('SELECT * FROM genres WHERE id = ?', (id,))
    genre = con.fetchone()
    if genre is None:
        return jsonify({'message': 'There is no genre with that ID'}), 400
    

    con.execute('DELETE FROM genres WHERE id = ?', (id,))
    connect.commit()
    return jsonify({'message': 'genre was deleted successfully'})


# see all authors
@app.route('/authors', methods=['GET'])
def get_all_authors():
    con.execute('SELECT * FROM authors')
    authors = con.fetchall()
    return jsonify([Author(*author).__json__() for author in authors])

# get author with specific id
@app.route('/authors/<int:id>', methods=['GET'])
def get_author_id(id):
    con.execute('SELECT * FROM authors WHERE id = ?', (id,))
    author = con.fetchone()
    if author is None:
        return jsonify({'message': 'There is no author with that ID'}), 400
    return jsonify(Author(*author).__json__())

# add new author
@app.route('/authors', methods=['POST'])
def create_new_author():
    name = request.json['name'].lower()

    
    con.execute('INSERT INTO authors (name) VALUES (?)', (name,))
    connect.commit()
    return jsonify({'message': 'author was created successfully'})

# change author info
@app.route('/authors/<int:id>', methods=['PUT'])
def update_author_info(id):
    name = request.json['name']

    #check if there is author with that id
    con.execute('SELECT * FROM authors WHERE id = ?', (id,))
    author = con.fetchone()
    if author is None:
        return jsonify({'message': 'There is no author with that ID'}), 400

    
    con.execute('UPDATE authors SET name = ? WHERE id = ?', (name, id))
    connect.commit()
    return jsonify({'message': 'author info was updated successfully'})

# Delete authors
@app.route('/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    #check if there is author with that id
    con.execute('SELECT * FROM authors WHERE id = ?', (id,))
    author = con.fetchone()
    if author is None:
        return jsonify({'message': 'There is no author with that ID'}), 400
    

    con.execute('DELETE FROM authors WHERE id = ?', (id,))
    connect.commit()
    return jsonify({'message': 'author was deleted successfully'})



# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)