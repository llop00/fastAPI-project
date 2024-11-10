# FastAPI Multi-Service Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9-3776AB.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10.0-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive backend service built with FastAPI, showcasing various API integrations, authentication, and modern backend development practices. This project serves as a demonstration of building scalable and maintainable microservices.

## Table of Contents

- [Features](#features)
- [Services](#services)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [Running with Docker](#running-with-docker)
  - [Running Locally](#running-locally)
  - [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- **FastAPI Framework**: High-performance async API development
- **Docker Integration**: Containerized deployment
- **Authentication**: JWT-based authentication system
- **Multiple Services**: Instagram posting, image generation, calculator
- **Email Integration**: Automated email notifications
- **External API Integration**: Freepik, ImgBB, Instagram
- **Comprehensive Logging**: Detailed system logging
- **Environment Management**: Secure configuration handling

## Services

- **Authentication Service**: JWT-based user authentication
- **Calculator API**: Mathematical operations endpoint
- **Image Generation**: AI-powered image generation using Freepik
- **Instagram Integration**: Automated Instagram posting
- **Image Hosting**: ImgBB integration for image storage
- **Email Service**: Automated email notifications

## Technologies Used

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern Python web framework
- **[Python 3.9](https://www.python.org/)**: Programming language
- **[Docker](https://www.docker.com/)**: Containerization
- **[Uvicorn](https://www.uvicorn.org/)**: ASGI web server
- **[PyJWT](https://pyjwt.readthedocs.io/)**: JWT authentication
- **[Requests](https://requests.readthedocs.io/)**: HTTP library
- **[Python-multipart](https://github.com/andrew-d/python-multipart)**: Form data parsing
- **[Python-dotenv](https://github.com/theskumar/python-dotenv)**: Environment management

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/fastapi-project.git
   cd fastapi-project
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create a `.env` file in the root directory:

```env
FREEPIK_API_KEY=your_freepik_key
INSTA_USER_ID=your_instagram_user_id
INSTA_ACCESS_TOKEN=your_instagram_access_token
IMGBB_API_KEY=your_imgbb_key
JWT_SECRET_KEY=your_jwt_secret
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

## Usage

### Running with Docker

```bash
docker-compose up --build
```

### Running Locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
fastapi-project/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── calculator.py
│   │   ├── freepik.py
│   │   ├── image_generator.py
│   │   ├── imgbb.py
│   │   └── instagram.py
│   ├── core/
│   │   └── config.py
│   └── utils/
│       └── email_utils.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## API Endpoints

- **Authentication**
  - `POST /auth/google`: Google authentication
  
- **Calculator**
  - `POST /calculator/calculate`: Perform calculations
  - `GET /calculator/operations`: List available operations

- **Image Services**
  - `POST /freepik/generate_image`: Generate images
  - `POST /imgbb/upload`: Upload images
  - `POST /instagram/upload_image`: Post to Instagram

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ using FastAPI and Python