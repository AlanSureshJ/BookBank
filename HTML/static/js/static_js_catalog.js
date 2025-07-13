document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const bookList = document.getElementById('book-list');

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = searchInput.value;
        searchBooks(query);
    });

    function searchBooks(query) {
        fetch(`/api/books/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(books => {
                displayBooks(books);
            })
            .catch(error => console.error('Error:', error));
    }

    function displayBooks(books) {
        bookList.innerHTML = '';
        books.forEach(book => {
            const bookElement = document.createElement('div');
            bookElement.className = 'book-item';
            bookElement.innerHTML = `
                <h3>${book.title}</h3>
                <p>Author: ${book.author}</p>
                <p>Genre: ${book.genre}</p>
                <button class="reserve-btn" data-book-id="${book.id}">Reserve</button>
            `;
            bookList.appendChild(bookElement);
        });

        // Add event listeners to reserve buttons
        document.querySelectorAll('.reserve-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const bookId = e.target.getAttribute('data-book-id');
                reserveBook(bookId);
            });
        });
    }

    function reserveBook(bookId) {
        fetch('/api/books/reserve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `book_id=${bookId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Book reserved successfully!');
            } else {
                alert('Failed to reserve book: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Load initial book list
    searchBooks('');
});