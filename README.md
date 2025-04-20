# CivicConnect

CivicConnect is a Django-based web application designed to facilitate civic engagement and grievance management. The platform leverages modern web technologies and AI capabilities to provide an efficient and user-friendly interface for handling civic concerns.

## Features

- **Grievance Management System**: Track and manage civic complaints and concerns
- **AI-Powered Analysis**: Utilizes natural language processing and machine learning for intelligent content analysis
- **User Authentication**: Secure user management system with JWT-based authentication
- **Media Handling**: Support for image uploads and processing
- **RESTful API**: Built with Django REST framework for seamless integration
- **Modern UI**: Responsive design with Bootstrap 5 and crispy forms

## Tech Stack

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, Crispy Forms
- **AI/ML**: 
  - Google Generative AI
  - scikit-learn
  - NLTK
  - Transformers
  - PyTorch
- **Database**: SQLite (Development)
- **Security**: JWT Authentication, bcrypt password hashing

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Msg-Python
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add necessary environment variables (refer to `.env.example` if available)

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

```
Msg-Python/
├── civic_connect/          # Main project configuration
├── grievances/            # Grievance management app
├── static/               # Static files (CSS, JS, images)
├── media/               # User-uploaded media files
├── nltk_data/          # NLTK data files
├── venv/              # Virtual environment
├── requirements.txt   # Project dependencies
└── manage.py         # Django management script
```

## Development

- Code formatting: `black`
- Linting: `flake8`
- Testing: `pytest`

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license here]

## Contact

[Add contact information] 