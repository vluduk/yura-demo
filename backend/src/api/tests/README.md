# Backend Unit Tests

This directory contains comprehensive unit tests for the backend of the project.

## Test Files

- **`test_auth.py`** - Tests for authentication (signup, login, logout, JWT tokens)
- **`test_advisor.py`** - Tests for the AI advisor service functionality
- **`test_models.py`** - Comprehensive tests for all database models
- **`test_views.py`** - Tests for all API views and endpoints
- **`test_serializers.py`** - Tests for DRF serializers
- **`test_services.py`** - Tests for service layer (AdvisorService)

## Running the Tests

### Using Docker (Recommended)

1. **Start the services:**
   ```bash
   make devUp
   # or
   docker compose up -d --build
   ```

2. **Run all tests:**
   ```bash
   docker compose exec backend python manage.py test
   ```

3. **Run specific test modules:**
   ```bash
   # Test models only
   docker compose exec backend python manage.py test api.tests.test_models
   
   # Test views only
   docker compose exec backend python manage.py test api.tests.test_views
   
   # Test serializers only
   docker compose exec backend python manage.py test api.tests.test_serializers
   
   # Test services only
   docker compose exec backend python manage.py test api.tests.test_services
   
   # Test authentication
   docker compose exec backend python manage.py test api.tests.test_auth
   
   # Test advisor
   docker compose exec backend python manage.py test api.tests.test_advisor
   ```

4. **Run with verbose output:**
   ```bash
   docker compose exec backend python manage.py test --verbosity=2
   ```

5. **Run specific test classes:**
   ```bash
   docker compose exec backend python manage.py test api.tests.test_models.UserModelTest
   ```

6. **Run specific test methods:**
   ```bash
   docker compose exec backend python manage.py test api.tests.test_models.UserModelTest.test_create_user_with_valid_data
   ```

### Using Virtual Environment (Alternative)

If you prefer to run tests locally without Docker:

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Navigate to backend source:**
   ```bash
   cd backend/src
   ```

3. **Run tests:**
   ```bash
   python manage.py test
   ```

## Test Coverage

### Models (`test_models.py`)
- ✅ User model (creation, validation, roles)
- ✅ Conversation model (CRUD, types, cascade delete)
- ✅ Message model (user/AI messages, relationships)
- ✅ BusinessIdea and ActionStep models
- ✅ Resume and all related models (Experience, Education, Skills, etc.)
- ✅ Article and ArticleCategory models
- ✅ Knowledge documents and categories
- ✅ UserAssessment model (answers sync, LLM context)

### Views (`test_views.py`)
- ✅ Authentication endpoints (signup, login, logout, /me)
- ✅ Conversation CRUD operations
- ✅ Chat functionality with AI
- ✅ Health check endpoint
- ✅ Permission checks
- ✅ Error handling

### Serializers (`test_serializers.py`)
- ✅ User serializers (registration, user info)
- ✅ Conversation serializer
- ✅ Message serializer
- ✅ Business idea serializers
- ✅ Resume serializers
- ✅ User assessment serializer
- ✅ Validation logic
- ✅ Read-only field protection

### Services (`test_services.py`)
- ✅ Knowledge base search
- ✅ Assessment context formatting
- ✅ LLM response processing
- ✅ Prompt building for different conversation types
- ✅ AI generation (initial messages, titles)
- ✅ Error handling
- ✅ System prompts configuration

### Authentication (`test_auth.py`)
- ✅ User signup flow
- ✅ Login with email/password
- ✅ JWT token handling
- ✅ Token refresh
- ✅ Logout and token blacklisting

### Advisor (`test_advisor.py`)
- ✅ Assessment question flow
- ✅ Response processing with JSON updates
- ✅ Conversation title generation
- ✅ Different conversation type handling
- ✅ Fallback behavior when LLM unavailable

## Test Statistics

Total test files: **6**
Total test classes: **40+**
Total test methods: **150+**

## Best Practices

- Tests use Django's TestCase for automatic database rollback
- Mock external services (Google AI) to avoid API calls during testing
- Each test is isolated and doesn't depend on others
- Comprehensive edge case and error handling coverage
- Tests both happy paths and failure scenarios

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Backend Tests
  run: |
    docker compose up -d
    docker compose exec -T backend python manage.py test --verbosity=2
```

## Troubleshooting

**Issue:** Tests fail with database errors
- **Solution:** Make sure Docker containers are running and database is migrated
  ```bash
  make migrate
  ```

**Issue:** Import errors in tests
- **Solution:** Ensure you're running tests from the correct directory and all dependencies are installed

**Issue:** Mock-related errors
- **Solution:** Check that unittest.mock patches are correctly applied and cleaned up

## Adding New Tests

When adding new functionality, please add corresponding tests:

1. Add test methods to existing test classes if testing existing components
2. Create new test classes for new components
3. Follow the naming convention: `test_<feature_description>`
4. Include docstrings explaining what each test validates
5. Update this README with new test coverage

## Code Coverage

To measure code coverage:

```bash
docker compose exec backend coverage run --source='.' manage.py test
docker compose exec backend coverage report
docker compose exec backend coverage html
```

This generates an HTML coverage report in `htmlcov/` directory.
