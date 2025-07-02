# 🚀 Live Deployment

## Backend API
- **Live URL**: https://be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net/
- **API Documentation**: https://be984984-aphkd5f2e7ake9ey.westeurope-01.azurewebsites.net/swagger

## Frontend Application
- **Live URL**: https://thankful-cliff-012dd3803.1.azurestaticapps.net/
- **Repository**: https://github.com/emreutkan/se3355website

---

# IMDB Clone API

A comprehensive movie database REST API with user authentication, ratings, reviews, and search functionality. Built with Flask and designed to handle both local development and Azure cloud deployment.

## Architecture & Design

### System Architecture

The application follows a **modular Flask architecture** with clear separation of concerns:

```
app/
├── models/          # SQLAlchemy data models
├── routes/          # API endpoints (Blueprint-based)
├── services/        # Business logic layer
├── utils/           # Utility functions and database helpers
└── config.py        # Configuration management
```

### Design Principles

- **RESTful API Design**: Clean, predictable endpoints following REST conventions
- **Blueprint Pattern**: Modular route organization for maintainability
- **Service Layer Pattern**: Business logic separated from route handlers
- **Configuration-based Deployment**: Environment-specific configurations
- **Database Agnostic**: Supports MySQL (local) and Azure SQL Database (production)

### Technology Stack

- **Backend Framework**: Flask 3.0.0
- **Database ORM**: SQLAlchemy 2.0.35 with Flask-SQLAlchemy
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **OAuth Integration**: Google OAuth 2.0
- **Database Migration**: Alembic via Flask-Migrate
- **API Documentation**: Swagger/OpenAPI via Flasgger
- **Database Drivers**: PyMySQL (MySQL), pyodbc (SQL Server)
- **Containerization**: Docker with Docker Compose

## Data Model

### Core Entities

#### Movies
```sql
movies (
    id: GUID (Primary Key)
    title: VARCHAR(255) -- Original title
    title_tr: VARCHAR(255) -- Turkish translation
    original_title: VARCHAR(255)
    year: SMALLINT
    summary: TEXT
    summary_tr: TEXT -- Turkish summary
    imdb_score: DECIMAL(3,1) -- Cached average rating
    metascore: SMALLINT
    trailer_url: TEXT
    image_url: TEXT
    runtime_min: SMALLINT
    release_date: DATE
    language: VARCHAR(30)
    created_at, updated_at: DATETIME
)
```

#### Users
```sql
users (
    id: GUID (Primary Key)
    email: VARCHAR(320) (Unique)
    password_hash: VARCHAR(255) -- NULL for OAuth users
    full_name: VARCHAR(120)
    country: VARCHAR(2) -- ISO-3166-1 alpha-2
    city: VARCHAR(80)
    photo_url: LONGTEXT
    auth_provider: ENUM('local', 'google')
    created_at, updated_at: DATETIME
)
```

#### Ratings
```sql
ratings (
    id: GUID (Primary Key)
    movie_id: GUID (Foreign Key)
    user_id: GUID (Foreign Key)
    rating: SMALLINT (1-10)
    comment: TEXT
    voter_country: VARCHAR(2)
    helpful_yes_count, helpful_no_count: SMALLINT
    created_at: DATETIME
)
```

#### Actors
```sql
actors (
    id: GUID (Primary Key)
    name: VARCHAR(255)
    birth_date: DATE
    death_date: DATE
    bio: TEXT
    bio_tr: TEXT -- Turkish biography
    photo_url: TEXT
    created_at, updated_at: DATETIME
)
```

### Relationships

- **Movies ↔ Actors**: Many-to-Many via `movie_actors` junction table
- **Movies ↔ Categories**: Many-to-Many via `movie_categories` junction table
- **Users ↔ Movies**: Many-to-Many via `ratings` (with additional rating data)
- **Users ↔ Movies**: Many-to-Many via `watchlist` (user's saved movies)
- **Movies → PopularitySnapshots**: One-to-Many (temporal popularity tracking)

### Key Design Decisions

1. **GUID Primary Keys**: Used UUIDs instead of auto-incrementing integers for better distributed system support and security
2. **Denormalized Ratings**: Cached average scores in movies table for performance
3. **Multi-language Support**: Separate fields for Turkish translations
4. **Soft Data Constraints**: Database-level constraints for data integrity
5. **Temporal Tracking**: Popularity snapshots for analytics and trending

## API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - User registration
- `POST /login` - Local authentication
- `GET /google` - Google OAuth initiation
- `GET /google/callback` - Google OAuth callback
- `POST /refresh` - JWT token refresh

### Movies (`/api/movies`)
- `GET /` - List movies with filtering/pagination
- `GET /{id}` - Get movie details
- `POST /{id}/rate` - Rate a movie
- `GET /{id}/ratings` - Get movie ratings
- `POST /` - Create movie (admin)
- `PUT /{id}` - Update movie (admin)

### Users (`/api/users`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile
- `GET /watchlist` - Get user's watchlist
- `POST /watchlist/{movie_id}` - Add to watchlist
- `DELETE /watchlist/{movie_id}` - Remove from watchlist

### Search (`/api/search`)
- `GET /movies` - Search movies by title, actors, etc.
- `GET /actors` - Search actors

### Actors (`/api/actors`)
- `GET /` - List actors
- `GET /{id}` - Get actor details
- `GET /{id}/movies` - Get actor's movies

## 🔧 Configuration & Deployment

### Environment Configuration

The application supports multiple deployment environments:

1. **Local Development** (MySQL)
2. **Azure Production** (SQL Database)

Configuration is managed through environment variables:

```bash
# Database Configuration
DB_SERVER_NAME=your-server.database.windows.net
DB_ADMIN_LOGIN=your-admin
DB_PASSWORD=your-password
DB_DATABASE_NAME=imdbapp

# Authentication
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Environment
API_ENVIRONMENT=production|local
```

### Docker Deployment

```bash
# Local development with PostgreSQL
docker-compose up -d

# Database initialization
python init_migrations.py
python setup_database.py

# Seed sample data
python scripts/seed_data.py
```

### Azure Deployment

The application is configured for Azure App Service deployment with:
- Azure SQL Database integration
- Environment-specific URL handling
- Production-ready logging and error handling

## 🎯 Key Features

### Authentication System
- **Dual Authentication**: Local accounts and Google OAuth
- **JWT-based**: Stateless authentication with refresh tokens
- **Role-based**: Extensible for admin/user roles

### Rating & Review System
- **1-10 Scale Rating**: Industry-standard scoring
- **Text Reviews**: Optional comments with ratings
- **Helpful Voting**: Community-driven review quality
- **Country-based Analytics**: Voter demographics tracking

### Search & Discovery
- **Full-text Search**: Movie titles, summaries, actor names
- **Advanced Filtering**: By year, genre, rating, etc.
- **Pagination Support**: Efficient large dataset handling

### Multi-language Support
- **Turkish Localization**: Translated titles and summaries
- **Language Detection**: Automatic content serving based on preferences

### Performance Optimizations
- **Database Indexing**: Strategic indexes on search fields
- **Cached Aggregations**: Pre-calculated average ratings
- **Connection Pooling**: Database connection optimization

## 🧩 Assumptions Made

### Business Logic Assumptions
1. **Rating Scale**: 1-10 integer ratings (following IMDB convention)
2. **Single Rating per User**: Users can rate each movie only once
3. **Public Profiles**: User ratings and reviews are publicly visible
4. **Immutable Ratings**: Ratings cannot be edited after submission
5. **English Primary**: English content is primary, Turkish is secondary

### Technical Assumptions
1. **GUID Collision**: UUID4 collision probability is negligible for our scale
2. **Database Performance**: Sub-100ms query response times for typical operations
3. **User Behavior**: Average user manages <100 watchlist items
4. **Content Volume**: Movie database scales to ~100K movies
5. **Concurrent Users**: System designed for <1K concurrent users

### Security Assumptions
1. **HTTPS Termination**: TLS handled by reverse proxy/load balancer
2. **Input Sanitization**: Client-side validation backed by server-side checks
3. **Rate Limiting**: Application-level rate limiting for API endpoints
4. **Token Security**: JWT tokens stored securely on client side

## 🐛 Problems Encountered & Solutions

### 1. Database Compatibility Issues

**Problem**: Supporting both MySQL (local) and SQL Server (Azure) with different SQL dialects.

**Solution**: 
- Used SQLAlchemy's database-agnostic ORM
- Implemented conditional connection strings in configuration
- Used appropriate database drivers (PyMySQL vs pyodbc)
- Avoided database-specific SQL in raw queries

### 2. GUID Implementation Challenges

**Problem**: SQLAlchemy UUID handling differs between database backends.

**Solution**:
- Created custom `GUID` column type that handles UUID serialization
- Implemented proper string representation for API responses
- Used `uuid.uuid4()` for consistent UUID generation

### 3. Google OAuth Integration

**Problem**: Complex OAuth flow with proper error handling and state management.

**Solution**:
- Implemented comprehensive OAuth service with state validation
- Added proper error handling for OAuth failures
- Created seamless user registration for new Google users
- Handled edge cases like existing email conflicts

### 4. Multi-environment Configuration

**Problem**: Managing different configurations for local vs Azure deployment.

**Solution**:
- Environment-based configuration classes
- Dynamic database URL generation
- Conditional feature flags based on environment
- Centralized configuration management

### 5. Database Migration Issues

**Problem**: Alembic migration compatibility between MySQL and SQL Server.

**Solution**:
- Created environment-specific migration scripts
- Used SQLAlchemy's database-agnostic column types
- Implemented careful constraint handling for both databases
- Added migration rollback capabilities

### 6. Performance with Large Datasets

**Problem**: Slow queries when searching through movies and ratings.

**Solution**:
- Added strategic database indexes on search columns
- Implemented pagination for large result sets
- Cached aggregate calculations (average ratings)
- Used query optimization techniques

### 7. API Documentation Maintenance

**Problem**: Keeping Swagger documentation in sync with actual API.

**Solution**:
- Used Flasgger for automatic documentation generation
- Implemented docstring-based API documentation
- Added comprehensive request/response examples
- Set up validation between docs and actual endpoints

### 8. Error Handling Consistency

**Problem**: Inconsistent error responses across different endpoints.

**Solution**:
- Implemented centralized error handlers
- Standardized error response format
- Added comprehensive logging for debugging
- Created user-friendly error messages

## 📈 Future Improvements

1. **Caching Layer**: Redis for frequently accessed data
2. **Search Enhancement**: Elasticsearch for advanced search capabilities
3. **Recommendation Engine**: ML-based movie recommendations
4. **Real-time Features**: WebSocket support for live updates
5. **Content Moderation**: Automated review content filtering
6. **Analytics Dashboard**: Admin panel for system metrics
7. **Mobile API**: Optimized endpoints for mobile applications
8. **Internationalization**: Support for additional languages

## 🛠️ Development Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd se3355finalbackend
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Database Setup**
   ```bash
   python init_migrations.py
   python setup_database.py
   python scripts/seed_data.py
   ```

5. **Run Application**
   ```bash
   python run.py
   ```

6. **Access API Documentation**
   - Open browser to `http://localhost:8000/swagger/`

## 📝 License

This project is developed for educational purposes as part of SE3355 course requirements.
