# Library Management System

A comprehensive web-based library management system built with Django. This application allows users to manage multiple libraries, books, loans, and user interactions in a modern and intuitive interface.

## Features

### User Management
- **Custom User Model**: Three types of users - Super Admin, Library Admin, and Reader
- **Authentication System**: Registration, login, logout, and profile management
- **Role-based Access Control**: Different permissions for different user types

### Library Management
- **Multiple Libraries**: Users can create and manage multiple libraries
- **Library Details**: Name, description, and ownership tracking
- **Library Administration**: Edit and delete libraries for authorized users

### Book Management
- **Book Catalog**: Add, edit, and delete books with detailed information
- **Book Information**: Title, author, ISBN, description, and cover image support
- **Availability Tracking**: Real-time book availability status
- **Book Requests**: Users can request books from other libraries
- **Book Notes**: Personal and public notes on books

### Loan Management
- **Book Lending**: Complete loan tracking system
- **Due Date Management**: Automatic due date calculation (14 days default)
- **Return Processing**: Book return functionality with date tracking
- **Overdue Tracking**: Automatic detection of overdue books
- **Loan History**: Complete borrowing and lending history

### Request System
- **Book Requests**: Request books from other users
- **Request Management**: Approve, reject, or cancel requests
- **Status Tracking**: Real-time request status updates
- **Messaging**: Optional messages with requests and responses

## Technology Stack

- **Backend**: Django 5.2+
- **Database**: SQLite (development), easily configurable for PostgreSQL/MySQL
- **Frontend**: HTML5, CSS3, JavaScript (with modern UI framework)
- **Image Processing**: Pillow for book cover images
- **Authentication**: Django's built-in authentication system with custom user model

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LibraryManagement
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv library_env
   source library_env/bin/activate  # On Windows: library_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to the Django project directory**
   ```bash
   cd LibraryManagement
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your web browser and go to `http://127.0.0.1:8000`

## Project Structure

```
LibraryManagement/
├── accounts/           # User management and authentication
├── books/             # Book management and requests
├── libraries/         # Library management
├── loans/             # Loan tracking and management
├── library_management/ # Main project settings
├── templates/         # HTML templates
├── static/           # Static files (CSS, JS, images)
├── media/            # User-uploaded files
└── manage.py         # Django management script
```

## Usage

### For Library Administrators
1. **Register** or **Login** to the system
2. **Create a Library** from the dashboard
3. **Add Books** to your library with details and cover images
4. **Manage Requests** from other users
5. **Track Loans** and returns
6. **View Analytics** on your dashboard

### For Readers
1. **Register** as a reader
2. **Browse Libraries** and books
3. **Request Books** from other users
4. **Manage Your Loans** - track borrowed and lent books
5. **Add Personal Notes** to books
6. **View Your Activity** on the dashboard

## Configuration

### Database Configuration
The project uses SQLite by default. To use PostgreSQL or MySQL:

1. Install the appropriate database adapter:
   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   # or
   pip install mysqlclient      # For MySQL
   ```

2. Update `DATABASES` in `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',  # or mysql
           'NAME': 'your_database_name',
           'USER': 'your_database_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',  # or 3306 for MySQL
       }
   }
   ```

### Media Files
Ensure the media directory has proper permissions for file uploads:
```bash
mkdir -p media/book_covers
chmod 755 media/
```

## API Endpoints

The application provides the following main URL patterns:
- `/` - Dashboard
- `/accounts/` - User authentication and profiles
- `/libraries/` - Library management
- `/books/` - Book catalog and requests
- `/loans/` - Loan management
- `/admin/` - Django admin interface

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For support, questions, or feature requests, please open an issue on the GitHub repository.

## Screenshots

*Note: Add screenshots of the application interface here*

---

**Built with ❤️ using Django**
