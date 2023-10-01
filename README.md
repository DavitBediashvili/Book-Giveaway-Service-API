# Book-Giveaway-Service-API

**Overview**

BookGive is a Python Flask application that allows users to manage their book collections. Users can register for an account, login, add books, edit book information, delete books, and browse a list of all books.

**Features**

* User registration and login
* Book management (add, edit, delete)
* Book browsing and filtering
* Genre and author management

**Requirements**

* Python 3.8+
* Flask
* SQLite3

**Installation**

1. Clone this repository:

```
git clone https://github.com/YOUR_USERNAME/bookgive.git
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Start the Flask development server:

```
python main.py
```

**Usage**

To use BookGive, simply visit the following URL in your web browser:

```
http://127.0.0.1:5000
```

You can then register for an account, login, and start managing your book collection.

**API documentation**

The following is a list of the available API endpoints:

* **GET /books:** Get a list of all books.
* **GET /books/<BOOK_ID>:** Get the book with the specified ID.
* **GET /books/genre/<GENRE>:** Get a list of all books with the specified genre.
* **GET /books/sorted_by/<SORT_BY>/<ASC_DESC>:** Get a list of all books sorted by the specified field, in the specified order.
* **POST /books:** Add a new book.
* **POST /books/<BOOK_ID>:** Edit the book with the specified ID.
* **DELETE /books/<BOOK_ID>:** Delete the book with the specified ID.
* **GET /genres:** Get a list of all genres.
* **GET /genres/<GENRE_ID>:** Get the genre with the specified ID.
* **POST /genres:** Create a new genre.
* **PUT /genres/<GENRE_ID>:** Edit the genre with the specified ID.
* **DELETE /genres/<GENRE_ID>:** Delete the genre with the specified ID.
* **GET /authors:** Get a list of all authors.
* **GET /authors/<AUTHOR_ID>:** Get the author with the specified ID.
* **POST /authors:** Create a new author.
* **PUT /authors/<AUTHOR_ID>:** Edit the author with the specified ID.
* **DELETE /authors/<AUTHOR_ID>:** Delete the author with the specified ID.

**Example usage**

```python
import requests

# Get a list of all books:
response = requests.get('http://localhost:5000/books')
books = response.json()

# Get the book with the ID 1:
response = requests.get('http://localhost:5000/books/1')
book = response.json()

# Get a list of all books with the genre "Fiction":
response = requests.get('http://localhost:5000/books/genre/Fiction')
books = response.json()

# Get a list of all books sorted by title in ascending order:
response = requests.get('http://localhost:5000/books/sorted_by/title/asc')
books = response.json()

# Add a new book:
response = requests.post('http://localhost:5000/books', json={
  "owner": "John Doe",
  "title": "The Hitchhiker's Guide to the Galaxy",
  "author": "Douglas Adams",
  "genre": "Science Fiction",
  "condition": "Good",
  "location": "New York City"
})

# Edit the book with the ID 1:
response = requests.post('http://localhost:5000/books/1', json={
  "title": "The Hitchhiker's Guide to the Galaxy (Revised Edition)"
})

# Delete the book with the ID 1:
response = requests.delete('http://localhost:5000/books/1')
```
