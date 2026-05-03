# Requirements Document: Render Deployment

## Introduction

This document specifies the requirements for deploying the SparePartFinder application to Render's cloud platform. The deployment encompasses a Flask backend API with PyTorch ML model, a React frontend SPA, database migration from SQLite to PostgreSQL, and complete production configuration. The deployment follows a structured pipeline: repository preparation → backend deployment → frontend deployment → service integration.

## Glossary

- **Backend_Service**: The Flask API application running on Render Web Service with PyTorch model inference capabilities
- **Frontend_Service**: The React SPA built with Vite and deployed as a Render Static Site
- **Render_Platform**: The cloud hosting platform providing Web Services and Static Sites
- **PORT_Variable**: The dynamic port environment variable provided by Render (required for backend binding)
- **API_URL**: The production backend URL that the frontend uses for HTTP requests
- **Model_File**: The spare_part_model.pth PyTorch weights file (approximately 14MB)
- **Database_Service**: PostgreSQL database instance on Render
- **Build_Command**: The command executed during deployment to prepare the application
- **Start_Command**: The command executed to run the application in production
- **Environment_Variables**: Configuration values injected at runtime (PORT, DATABASE_URL, API keys)
- **CORS_Configuration**: Cross-Origin Resource Sharing settings allowing frontend-backend communication
- **Static_Assets**: The AutoMobile_Dataset directory and classes.json file required by the model
- **Health_Check**: HTTP endpoint verification that the service is running correctly

## Requirements

### Requirement 1: Repository Preparation

**User Story:** As a developer, I want to prepare the repository for deployment, so that Render can successfully build and deploy both services.

#### Acceptance Criteria

1. THE Backend_Service SHALL include a requirements.txt file with all Python dependencies pinned to specific versions
2. THE Backend_Service SHALL include a Procfile or render.yaml specifying the Start_Command using gunicorn
3. THE Frontend_Service SHALL include a package.json with build scripts configured for production
4. THE Model_File SHALL be committed to the repository and accessible at the root level
5. THE Static_Assets SHALL be committed to the repository in their current directory structure
6. WHEN the repository is pushed to GitHub, THE Render_Platform SHALL have access to all required files

### Requirement 2: Backend Port Configuration

**User Story:** As a backend service, I want to bind to the dynamic port provided by Render, so that the platform can route traffic to my application.

#### Acceptance Criteria

1. WHEN the Backend_Service starts, THE application SHALL read the PORT_Variable from environment variables
2. IF the PORT_Variable is not set, THEN THE Backend_Service SHALL default to port 5000 for local development
3. THE Backend_Service SHALL bind to host 0.0.0.0 to accept external connections
4. WHEN Render assigns a port, THE Backend_Service SHALL listen on that port within 60 seconds
5. THE Start_Command SHALL use gunicorn with the format "gunicorn app:app --bind 0.0.0.0:$PORT"

### Requirement 3: Database Migration

**User Story:** As a backend service, I want to use PostgreSQL in production, so that I have a reliable production-grade database.

#### Acceptance Criteria

1. WHEN USE_POSTGRES environment variable is "true", THE Backend_Service SHALL connect to PostgreSQL using DATABASE_URL
2. WHEN USE_POSTGRES environment variable is "false" or unset, THE Backend_Service SHALL connect to SQLite for local development
3. THE Backend_Service SHALL create all required database tables on first startup using db.create_all()
4. WHEN DATABASE_URL contains "postgres://", THE Backend_Service SHALL replace it with "postgresql://" for SQLAlchemy compatibility
5. THE Database_Service SHALL persist data across Backend_Service restarts

### Requirement 4: Backend Deployment Configuration

**User Story:** As a developer, I want to configure the backend service on Render, so that it runs with correct settings and dependencies.

#### Acceptance Criteria

1. THE Backend_Service SHALL be deployed as a Render Web Service (not Static Site)
2. THE Build_Command SHALL be "pip install -r requirements.txt"
3. THE Start_Command SHALL be "gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120"
4. THE Backend_Service SHALL set Environment_Variables: USE_POSTGRES=true, DATABASE_URL (from Render PostgreSQL), FLASK_ENV=production
5. THE Backend_Service SHALL have a Health_Check endpoint at "/" or "/api/analytics" returning HTTP 200
6. WHEN dependencies are installed, THE Backend_Service SHALL include torch, torchvision, Flask, gunicorn, psycopg2-binary, and beautifulsoup4

### Requirement 5: Frontend Build Configuration

**User Story:** As a frontend application, I want to be built with the correct API URL, so that I can communicate with the deployed backend.

#### Acceptance Criteria

1. THE Frontend_Service SHALL replace localhost API URLs with the production API_URL during build
2. WHEN building for production, THE Frontend_Service SHALL use "npm run build" or "vite build"
3. THE Frontend_Service SHALL output static files to the "dist" directory
4. THE Frontend_Service SHALL include all dependencies from package.json in the build
5. WHEN the build completes, THE Frontend_Service SHALL contain index.html, JavaScript bundles, and CSS files in the dist directory

### Requirement 6: Frontend Deployment Configuration

**User Story:** As a developer, I want to deploy the frontend as a static site, so that users can access the application interface.

#### Acceptance Criteria

1. THE Frontend_Service SHALL be deployed as a Render Static Site
2. THE Build_Command SHALL be "cd frontend && npm install && npm run build"
3. THE Publish_Directory SHALL be "frontend/dist"
4. THE Frontend_Service SHALL serve index.html for all routes (SPA routing support)
5. WHEN a user navigates to the Frontend_Service URL, THE application SHALL load within 3 seconds

### Requirement 7: CORS Configuration

**User Story:** As a backend service, I want to allow cross-origin requests from the frontend, so that the browser permits API calls.

#### Acceptance Criteria

1. THE CORS_Configuration SHALL allow requests from the Frontend_Service domain
2. THE CORS_Configuration SHALL allow requests from localhost origins for development
3. THE CORS_Configuration SHALL permit GET, POST, PUT, DELETE, OPTIONS methods
4. THE CORS_Configuration SHALL allow Content-Type and Authorization headers
5. WHEN the Frontend_Service makes an API request, THE Backend_Service SHALL respond with appropriate CORS headers

### Requirement 8: Environment Variables Management

**User Story:** As a developer, I want to manage environment-specific configuration, so that the application behaves correctly in production.

#### Acceptance Criteria

1. THE Backend_Service SHALL read PORT_Variable from os.environ.get('PORT', 5000)
2. THE Backend_Service SHALL read DATABASE_URL from environment variables when USE_POSTGRES is true
3. THE Backend_Service SHALL set FLASK_ENV to "production" in Render environment
4. THE Frontend_Service SHALL use VITE_API_URL environment variable if provided, otherwise use hardcoded production URL
5. WHEN Environment_Variables are updated in Render dashboard, THE services SHALL use new values after restart

### Requirement 9: Static Assets Availability

**User Story:** As a backend service, I want to access the model file and dataset, so that I can perform image classification.

#### Acceptance Criteria

1. WHEN the Backend_Service starts, THE Model_File SHALL be loadable from the root directory
2. WHEN the Backend_Service starts, THE classes.json file SHALL be readable from the root directory
3. THE Backend_Service SHALL create the "static/uploads" directory if it does not exist
4. THE AutoMobile_Dataset directory SHALL be accessible for any dataset-dependent operations
5. WHEN loading the model, THE Backend_Service SHALL use map_location=torch.device('cpu') for CPU inference

### Requirement 10: Service Health Monitoring

**User Story:** As a platform operator, I want to monitor service health, so that I can detect and respond to failures.

#### Acceptance Criteria

1. THE Backend_Service SHALL respond to GET requests at "/api/analytics" with HTTP 200 when healthy
2. THE Backend_Service SHALL respond within 5 seconds to health check requests
3. WHEN the Backend_Service is unhealthy, THE Render_Platform SHALL restart the service automatically
4. THE Frontend_Service SHALL return HTTP 200 for the root path "/" when healthy
5. WHEN either service fails health checks for 3 consecutive minutes, THE Render_Platform SHALL send an alert

### Requirement 11: Database Initialization

**User Story:** As a backend service, I want to initialize the database schema on first deployment, so that the application can store data.

#### Acceptance Criteria

1. WHEN the Backend_Service connects to an empty Database_Service, THE application SHALL create all tables using db.create_all()
2. THE Backend_Service SHALL create tables for Part and PriceRecord models
3. WHEN the "/api/init-database" endpoint is called, THE Backend_Service SHALL populate sample parts data
4. THE database initialization SHALL complete within 30 seconds
5. WHEN tables already exist, THE Backend_Service SHALL not drop or recreate them

### Requirement 12: Frontend-Backend Integration

**User Story:** As a frontend application, I want to connect to the backend API, so that I can upload images and retrieve predictions.

#### Acceptance Criteria

1. THE Frontend_Service SHALL send POST requests to API_URL + "/predict" with multipart/form-data
2. THE Frontend_Service SHALL send GET requests to API_URL + "/api/parts" for inventory data
3. THE Frontend_Service SHALL send GET requests to API_URL + "/api/analytics" for statistics
4. WHEN the Backend_Service is unavailable, THE Frontend_Service SHALL display a user-friendly error message
5. THE Frontend_Service SHALL include the full API_URL in all HTTP requests (not relative paths)

### Requirement 13: Deployment Pipeline Execution

**User Story:** As a developer, I want to follow a structured deployment process, so that both services are deployed correctly and in the right order.

#### Acceptance Criteria

1. THE deployment pipeline SHALL follow the sequence: repository preparation → backend deployment → frontend deployment → integration testing
2. WHEN the repository is pushed, THE developer SHALL connect it to Render via GitHub integration
3. THE Backend_Service SHALL be deployed and verified before deploying the Frontend_Service
4. WHEN the Backend_Service is running, THE developer SHALL obtain the API_URL for frontend configuration
5. THE Frontend_Service SHALL be deployed with the correct API_URL environment variable or hardcoded value

### Requirement 14: Production Security Configuration

**User Story:** As a security-conscious developer, I want to configure production security settings, so that the application is protected against common vulnerabilities.

#### Acceptance Criteria

1. THE Backend_Service SHALL set FLASK_ENV to "production" (disables debug mode)
2. THE Backend_Service SHALL not expose detailed error messages to clients in production
3. THE Backend_Service SHALL validate file uploads for allowed extensions (png, jpg, jpeg)
4. THE Backend_Service SHALL enforce MAX_CONTENT_LENGTH of 16MB for uploads
5. THE Backend_Service SHALL use secure_filename() for all uploaded file names

### Requirement 15: Build Optimization

**User Story:** As a developer, I want optimized build processes, so that deployments complete quickly and efficiently.

#### Acceptance Criteria

1. THE Backend_Service build SHALL complete within 5 minutes on Render's infrastructure
2. THE Frontend_Service build SHALL complete within 3 minutes on Render's infrastructure
3. THE Backend_Service SHALL use pip caching to speed up dependency installation
4. THE Frontend_Service SHALL use npm caching to speed up dependency installation
5. WHEN builds fail, THE Render_Platform SHALL display clear error messages in the deployment logs

### Requirement 16: Logging and Debugging

**User Story:** As a developer, I want comprehensive logging, so that I can diagnose issues in production.

#### Acceptance Criteria

1. THE Backend_Service SHALL log all incoming requests with timestamp and endpoint
2. THE Backend_Service SHALL log database connection status on startup
3. THE Backend_Service SHALL log model loading success or failure
4. THE Backend_Service SHALL log scraping statistics and failures
5. WHEN errors occur, THE Backend_Service SHALL log stack traces to Render's log stream

### Requirement 17: Gunicorn Configuration

**User Story:** As a production backend, I want to run with a production WSGI server, so that I can handle concurrent requests efficiently.

#### Acceptance Criteria

1. THE Backend_Service SHALL use gunicorn instead of Flask's development server
2. THE gunicorn configuration SHALL set timeout to 120 seconds for ML inference operations
3. THE gunicorn configuration SHALL bind to 0.0.0.0:$PORT
4. THE gunicorn configuration SHALL use the default number of workers (1 worker for free tier)
5. WHEN gunicorn starts, THE Backend_Service SHALL log "Booting worker" messages

### Requirement 18: Database URL Compatibility

**User Story:** As a backend service, I want to handle Render's PostgreSQL URL format, so that I can connect successfully.

#### Acceptance Criteria

1. WHEN DATABASE_URL starts with "postgres://", THE Backend_Service SHALL replace it with "postgresql://"
2. THE Backend_Service SHALL parse the DATABASE_URL for host, port, database name, username, and password
3. WHEN the database connection fails, THE Backend_Service SHALL log the error and retry up to 3 times
4. THE Backend_Service SHALL wait 5 seconds between connection retry attempts
5. WHEN all connection attempts fail, THE Backend_Service SHALL exit with a non-zero status code

### Requirement 19: Model Loading Robustness

**User Story:** As a backend service, I want to load the PyTorch model reliably, so that predictions work in production.

#### Acceptance Criteria

1. WHEN the Backend_Service starts, THE application SHALL attempt to load spare_part_model.pth
2. THE model loading SHALL use map_location=torch.device('cpu') for CPU-only inference
3. THE model loading SHALL handle both Sequential classifier format (with Dropout) and Linear-only format
4. WHEN the model file is missing, THE Backend_Service SHALL log an error and exit
5. WHEN the model loads successfully, THE Backend_Service SHALL log "Model loaded successfully"

### Requirement 20: Post-Deployment Verification

**User Story:** As a developer, I want to verify the deployment, so that I can confirm all features work correctly in production.

#### Acceptance Criteria

1. THE developer SHALL verify the Frontend_Service loads at its Render URL
2. THE developer SHALL verify the Backend_Service responds to GET /api/analytics
3. THE developer SHALL verify image upload and prediction functionality works end-to-end
4. THE developer SHALL verify price scraping returns results from external retailers
5. THE developer SHALL verify database operations (create, read) work with PostgreSQL
