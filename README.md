# Roadmap Learner API

A modern backend service for managing learning roadmaps with built-in authentication, authorization, and a comprehensive REST API. This project is designed to help users organize their learning journey through structured roadmaps, blocks, and learning cards.

## 📋 Overview

**Roadmap Learner API** is a FastAPI-based backend service that provides:
- User authentication and authorization
- Learning roadmap management
- Structured learning blocks and cards
- Learning session tracking
- Redis-based caching
- PostgreSQL data persistence
- Comprehensive REST API with filtering and pagination

## 🛠 Technology Stack

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Modern async web framework for building APIs |
| **SQLAlchemy 2.0** | Object-relational mapper with async support |
| **PostgreSQL** | Primary relational database |
| **Redis** | Caching and session management |
| **Alembic** | Database migration management |
| **FastAPI-Users** | Complete authentication and authorization system |
| **Pydantic** | Data validation and serialization |
| **Docker** | Containerization and orchestration |
| **Asyncpg** | Fast async PostgreSQL driver |

## 📦 Data Models

The application manages the following core entities:

- **User** - System users with authentication and profile information
- **Roadmap** - Learning roadmaps that organize educational content
- **Block** - Sections within a roadmap containing related learning material
- **Card** - Individual learning cards/lessons within a block
- **Session** - User learning sessions for tracking progress
- **AccessToken** - Token management for API authentication

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis 8+ (or use Docker)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/roadmap-learner-api.git
   cd roadmap-learner-api
   ```

2. **Create environment file**
   ```bash
   # Create .env file with required configuration
   # Example variables:
   # APP_CONFIG__DB__USERNAME=postgres
   # APP_CONFIG__DB__PASSWORD=password
   # APP_CONFIG__DB__NAME=roadmap_db
   # APP_CONFIG__RUN__HOST=0.0.0.0
   # APP_CONFIG__RUN__PORT=8000
   ```

3. **Install dependencies** (using pip)
   ```bash
   pip install -r requirements.txt
   ```

   Or using `uv` (optional, faster):
   ```bash
   uv sync
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the FastAPI application
   - Start PostgreSQL database
   - Start Redis cache
   - Initialize the database

2. **Access the application**
   - API Documentation: `http://localhost:8080/docs`
   - Health Check: `http://localhost:8080/health`

## 📚 API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with credentials
- `POST /auth/logout` - Logout current user
- `GET /auth/me` - Get current user info

### Users
- `GET /users` - List all users
- `GET /users/{user_id}` - Get specific user
- `PATCH /users/{user_id}` - Update user profile

### Roadmaps
- `GET /roadmaps` - List all roadmaps
- `GET /roadmaps/filters` - Filter roadmaps
- `GET /roadmaps/{roadmap_id}` - Get specific roadmap
- `POST /roadmaps` - Create new roadmap
- `PATCH /roadmaps/{roadmap_id}` - Update roadmap
- `DELETE /roadmaps/{roadmap_id}` - Delete roadmap

### Blocks
- `GET /blocks` - List all blocks
- `GET /blocks/filters` - Filter blocks
- `GET /blocks/{block_id}` - Get specific block
- `POST /blocks` - Create new block
- `PATCH /blocks/{block_id}` - Update block
- `DELETE /blocks/{block_id}` - Delete block

### Cards
- `GET /cards` - List all cards
- `GET /cards/filters` - Filter cards by block
- `GET /cards/{card_id}` - Get specific card
- `POST /cards` - Create new card
- `PATCH /cards/{card_id}` - Update card
- `DELETE /cards/{card_id}` - Delete card

### Sessions
- `GET /sessions` - List user learning sessions
- `POST /sessions` - Create new session
- `PATCH /sessions/{session_id}` - Update session

## 📂 Project Structure

```
roadmap-learner-api/
├── app/
│   ├── api/                    # API routes and endpoints
│   │   └── v1/                # API v1 endpoints
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── user.py        # User management
│   │       ├── roadmap.py     # Roadmap management
│   │       ├── block.py       # Block management
│   │       ├── card.py        # Card management
│   │       └── session.py     # Session management
│   ├── core/                  # Core application logic
│   │   ├── config.py          # Configuration management
│   │   ├── authentication/    # Authentication helpers
│   │   ├── cache/             # Redis cache helpers
│   │   ├── dependencies/      # Dependency injection
│   │   └── handlers.py        # Request handlers
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── roadmap.py
│   │   ├── block.py
│   │   ├── card.py
│   │   ├── session.py
│   │   └── access_token.py
│   ├── services/              # Business logic
│   │   ├── user.py
│   │   ├── roadmap.py
│   │   ├── block.py
│   │   ├── card.py
│   │   └── session.py
│   ├── repositories/          # Data access layer
│   │   ├── user.py
│   │   ├── roadmap.py
│   │   ├── block.py
│   │   ├── card.py
│   │   └── session.py
│   ├── schemas/               # Pydantic validation schemas
│   │   ├── user.py
│   │   ├── roadmap.py
│   │   ├── block.py
│   │   ├── card.py
│   │   └── session.py
│   └── utils/                 # Utility functions
├── alembic/                   # Database migrations
│   └── versions/              # Migration files
├── tests/                     # Test suite
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project configuration
├── Dockerfile                 # Docker image configuration
├── docker-compose.yml         # Docker Compose configuration
└── README.md                  # This file
```

## ⚙️ Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Database Configuration
APP_CONFIG__DB__USERNAME=postgres
APP_CONFIG__DB__PASSWORD=your_secure_password
APP_CONFIG__DB__NAME=roadmap_db
APP_CONFIG__DB__HOST=localhost
APP_CONFIG__DB__PORT=5432

# Redis Configuration
APP_CONFIG__REDIS__URL=redis://localhost:6379

# Server Configuration
APP_CONFIG__RUN__HOST=0.0.0.0
APP_CONFIG__RUN__PORT=8000

# API Configuration
APP_CONFIG__API__V1__PREFIX=/api/v1
```

## 🗄️ Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

Run specific test file:
```bash
pytest tests/test_api/test_roadmap.py
```

## 📝 Code Quality

The project uses several tools for code quality:

- **Ruff** - Fast Python linter
- **MyPy** - Static type checker

Check code quality:
```bash
ruff check .
mypy app/
```

Fix code issues:
```bash
ruff check --fix .
```

## 🔐 Security Considerations

- User authentication is handled by **FastAPI-Users** with secure password hashing
- API endpoints require authentication via HTTP Bearer tokens
- CORS is configured for specific origins (configurable in `main.py`)
- Database credentials are managed through environment variables
- Access tokens have expiration times

## 🚦 Health Check

Check if the API is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "active"}
```

## 📖 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs``

## 📦 Dependencies

### Core Dependencies
- fastapi >= 0.117.1
- sqlalchemy >= 2.0.43
- asyncpg >= 0.30.0
- pydantic >= 2.11.9
- fastapi-users[oauth,sqlalchemy] >= 15.0.1
- redis >= 5.0.0
- uvicorn >= 0.37.0
- alembic >= 1.17.1

### Development Dependencies
- pytest
- ruff
- mypy


