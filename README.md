
# Academic Performance Analysis Dashboard

This Django project is designed to analyze and visualize academic performance metrics, including component performance, grade distribution, and course analysis.

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- Virtual Environment (recommended)

## Installation Steps

1. **Clone the Repository**  
   Clone the project repository from GitHub:
   ```bash
   git clone https://github.com/Amiradha/Major.git
   cd Major
   ```

2. **Create and Activate Virtual Environment**  
   - On **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - On **Linux/MacOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**  
   Install all required dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**  
   - Install MySQL Server.
   - Create a new MySQL database.
   - Update database settings in `settings.py` with your credentials:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'your_database_name',
             'USER': 'your_mysql_username',
             'PASSWORD': 'your_mysql_password',
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }
     ```

5. **Apply Migrations**  
   Run the following commands to set up your database schema:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run the Development Server**  
   Start the development server:
   ```bash
   python manage.py runserver
   ```
   The application will be accessible at `http://127.0.0.1:8000/`.

---

## Features

- Component Performance Analysis
- Grade Distribution Visualization
- Course Performance Tracking
- Interactive Charts and Graphs
- User Authentication
- Responsive Design

## Project Structure

```
Major_Project/
├── academic/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── static/
├── manage.py
└── requirements.txt
```

---

## Dependencies

```
Django
asgiref
sqlparse
tzdata
mysqlclient
python-dotenv
django-tailwind
django-debug-toolbar
django-extensions
pytest
pytest-django
gunicorn
whitenoise
```

---

## Troubleshooting

1. **MySQLdb Error**:
   - Ensure MySQL is installed.
   - Install `mysqlclient`:
     ```bash
     pip install mysqlclient
     ```

2. **Database Connection**:
   - Ensure the MySQL server is running.
   - Double-check the database credentials in `settings.py`.

3. **Static Files**:
   - Run:
     ```bash
     python manage.py collectstatic
     ```
   - Ensure `STATIC_ROOT` is configured in `settings.py`.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit and push your changes.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License.

Let me know if there's anything else you'd like to include!
