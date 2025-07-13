document.addEventListener('DOMContentLoaded', () => {
    const exchangeList = document.getElementById('exchange-list');
    const myBooksList = document.getElementById('my-books');

    function loadExchangeableBooks() {
        fetch('/api/books?status=available')
            .then(response => response.json())
            .then(books => {
                displayExchangeableBooks(books);
            })
            .catch(error => console.error('Error:', error));
    }

    function displayExchangeableBooks(books) {
        exchangeList.innerHTML = '';
        books.forEach(book => {
            const bookElement = document.createElement('div');
            bookElement.className = 'book-item';
            bookElement.innerHTML = `
                <h3>${book.title}</h3>
                <p>Author: ${book.author}</p>
                <p>Genre: ${book.genre}</p>
                <button class="exchange-btn" data-book-id="${book.id}">Exchange</button>
            `;
            exchangeList.appendChild(bookElement);
        });

        // Add event listeners to exchange buttons
        document.querySelectorAll('.exchange-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const bookId = e.target.getAttribute('data-book-id');
                exchangeBook(bookId);
            });
        });
    }

    function exchangeBook(bookId) {
        fetch('/api/books/exchange', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `book_id=${bookId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Book exchanged successfully!');
                loadExchangeableBooks();
                loadMyBooks();
            } else {
                alert('Failed to exchange book: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function loadMyBooks() {
        fetch('/api/books?owner=current_user')
            .then(response => response.json())
            .then(books => {
                displayMyBooks(books);
            })
            .catch(error => console.error('Error:', error));
    }

    function displayMyBooks(books) {
        myBooksList.innerHTML = '';
        books.forEach(book => {
            const bookElement = document.createElement('div');
            bookElement.className = 'book-item';
            bookElement.innerHTML = `
                <h3>${book.title}</h3>
                <p>Author: ${book.author}</p>
                <p>Genre: ${book.genre}</p>
                <p>Status: ${book.status}</p>
            `;
            myBooksList.appendChild(bookElement);
        });
    }

    loadExchangeableBooks();
    loadMyBooks();
});