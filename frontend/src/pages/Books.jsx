import React, { useState, useEffect } from 'react';
import api from '../api';

function BooksPage() {
  const [books, setBooks] = useState([]);
  const [newBook, setNewBook] = useState({ title: '', author: '', isbn: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await api.get('/books/');
      setBooks(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch books.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBook = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/books/', newBook);
      setNewBook({ title: '', author: '', isbn: '' });
      fetchBooks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create book.');
      console.error(err);
    }
  };

  if (loading) return <div className="text-center mt-8">Loading books...</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Books</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">{error}</div>}

      <div className="mb-8 p-6 bg-white shadow-md rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Add New Book</h2>
        <form onSubmit={handleCreateBook} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
            <input
              type="text"
              id="title"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newBook.title}
              onChange={(e) => setNewBook({ ...newBook, title: e.target.value })}
              required
            />
          </div>
          <div>
            <label htmlFor="author" className="block text-sm font-medium text-gray-700">Author</label>
            <input
              type="text"
              id="author"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newBook.author}
              onChange={(e) => setNewBook({ ...newBook, author: e.target.value })}
              required
            />
          </div>
          <div>
            <label htmlFor="isbn" className="block text-sm font-medium text-gray-700">ISBN</label>
            <input
              type="text"
              id="isbn"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              value={newBook.isbn}
              onChange={(e) => setNewBook({ ...newBook, isbn: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Create Book
          </button>
        </form>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4">All Books</h2>
        {books.length === 0 ? (
          <p>No books found.</p>
        ) : (
          <ul className="divide-y divide-gray-200">
            {books.map((book) => (
              <li key={book.id} className="py-4 flex justify-between items-center">
                <div>
                  <p className="text-lg font-medium text-gray-900">{book.title} by {book.author}</p>
                  <p className="text-sm text-gray-500">ISBN: {book.isbn} - Status: <span className={`font-semibold ${book.status === 'Available' ? 'text-green-600' : book.status === 'Borrowed' ? 'text-red-600' : 'text-yellow-600'}`}>{book.status}</span></p>
                </div>
                <span className="text-xs text-gray-400">ID: {book.id.substring(0, 8)}...</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default BooksPage;
