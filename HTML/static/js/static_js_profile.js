document.addEventListener('DOMContentLoaded', () => {
    const userInfo = document.getElementById('user-info');
    const borrowedBooks = document.getElementById('borrowed-books');
    const exchangeHistory = document.getElementById('exchange-history');

    function loadUserInfo() {
        fetch('/api/user/info')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    userInfo.innerHTML = `
                        <h3>Welcome, ${data.username}!</h3>
                        <p>Email: ${data.email}</p>
                        <p>Points: ${data.points}</p>
                    `;
                } else {
                    userInfo.innerHTML = '<p>Failed to load user information.</p>';
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function loadBorrowedBooks() {
        fetch('/api/books?status=borrowed&user=current')
            .then(response => response.json())
            .then(books => {
                borrowedBooks.innerHTML = '<h3>Borrowed Books</h3>';
                if (books.length === 0) {
                    borrowedBooks.innerHTML += '<p>No books currently borrowed.</p>';
                } else {
                    const ul = document.createElement('ul');
                    books.forEach(book => {
                        const li = document.createElement('li');
                        li.textContent = `${book.title} by ${book.author}`;
                        ul.appendChild(li);
                    });
                    borrowedBooks.appendChild(ul);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function loadExchangeHistory() {
        fetch('/api/transactions?type=exchange&user=current')
            .then(response => response.json())
            .then(transactions => {
                exchangeHistory.innerHTML = '<h3>Exchange History</h3>';
                if (transactions.length === 0) {
                    exchangeHistory.innerHTML += '<p>No exchange history found.</p>';
                } else {
                    const ul = document.createElement('ul');
                    transactions.forEach(transaction => {
                        const li = document.createElement('li');
                        li.textContent = `${transaction.book_title} - ${transaction.transaction_date}`;
                        ul.appendChild(li);
                    });
                    exchangeHistory.appendChild(ul);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    loadUserInfo();
    loadBorrowedBooks();
    loadExchangeHistory();
});