# SponsorSync - Student Club Sponsorship Platform

## Overview

SponsorSync is an AI-powered web platform that connects student clubs with sponsors for meaningful partnerships. The platform uses machine learning algorithms to match events with appropriate sponsors based on various criteria including audience demographics, location, industry alignment, and content similarity.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with PostgreSQL (configured via DATABASE_URL environment variable)
- **Authentication**: Flask-Login for session management
- **AI/ML**: scikit-learn for text similarity matching using TF-IDF vectorization and cosine similarity

### Frontend Architecture
- **Templates**: Jinja2 templating engine with Bootstrap 5 dark theme
- **CSS Framework**: Bootstrap 5 with custom CSS enhancements
- **JavaScript**: Vanilla JavaScript for interactive features
- **Icons**: Font Awesome for consistent iconography

### Application Structure
- **Models**: SQLAlchemy models for User, ClubProfile, SponsorProfile, Event, Message, and SponsorInterest
- **Forms**: WTForms for form handling and validation
- **Routes**: Flask routes handling authentication, profiles, events, and messaging
- **AI Matching**: Custom AIMatchmaker class for intelligent sponsor-event matching

## Key Components

### User Management
- **Two-tier user system**: Clubs and Sponsors with different capabilities
- **Profile management**: Separate profile forms and data models for clubs and sponsors
- **Authentication**: Username/password authentication with session management

### Event Management
- **Event creation**: Clubs can create events with detailed information
- **Event discovery**: Sponsors can search and filter events
- **Event details**: Comprehensive event pages with sponsor requirements

### AI Matching System
- **Text similarity**: TF-IDF vectorization with cosine similarity for content matching
- **Multi-factor scoring**: Combines tag similarity (40%), audience overlap (25%), location relevance (20%), and industry alignment (15%)
- **Smart recommendations**: AI-powered suggestions for sponsor-event partnerships

### Messaging System
- **Direct communication**: Built-in messaging between clubs and sponsors
- **Interest tracking**: System for sponsors to express interest in events

### Search and Discovery
- **Advanced filtering**: Keyword, location, and date-based event search
- **Match scoring**: AI-calculated compatibility scores displayed to users

## Data Flow

1. **User Registration**: Users sign up as either club or sponsor
2. **Profile Creation**: Users complete detailed profiles with preferences and requirements
3. **Event Publishing**: Clubs create and publish events seeking sponsorship
4. **AI Matching**: System calculates match scores between events and sponsors
5. **Discovery**: Sponsors search events, view match scores, and explore opportunities
6. **Communication**: Interested parties connect through built-in messaging
7. **Partnership**: Successful matches lead to sponsorship partnerships

## External Dependencies

### Python Packages
- **Flask**: Web framework and extensions (SQLAlchemy, Login, WTF)
- **scikit-learn**: Machine learning library for text analysis
- **pandas**: Data manipulation for AI processing
- **numpy**: Numerical computations
- **Werkzeug**: WSGI utilities and security

### Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: No additional frontend frameworks

### Infrastructure
- **Database**: PostgreSQL (via DATABASE_URL environment variable)
- **Session Management**: Flask sessions with secret key
- **Environment Variables**: Configuration through environment variables

## Deployment Strategy

### Configuration
- **Environment-based**: Uses environment variables for database URL and session secrets
- **WSGI-ready**: Configured with ProxyFix for deployment behind reverse proxies
- **Database initialization**: Automatic table creation on startup

### Development Setup
- **Debug mode**: Enabled for development with detailed error logging
- **Hot reload**: Flask development server with automatic reloading
- **Logging**: Comprehensive logging for debugging and monitoring

### Production Considerations
- **Database pooling**: Connection pool management with recycle and pre-ping
- **Security**: Password hashing with Werkzeug security utilities
- **Session security**: Secure session management with secret keys

The platform is designed to be scalable and maintainable, with clear separation of concerns between data models, business logic, and presentation layers. The AI matching system provides intelligent recommendations while maintaining simple, user-friendly interfaces for both clubs and sponsors.