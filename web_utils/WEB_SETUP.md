# StressSpec Web UI Setup Guide

This guide helps you set up the web interface for StressSpec.

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 2. Setup Web UI
```bash
# Run the automated setup script
python setup_web.py
```

This script will:
- Create the web directory structure
- Install all required dependencies
- Download HTMX library
- Create environment configuration
- Verify the setup

### 3. Start Development Server
```bash
# Start the development server
python run_web.py
```

The web interface will be available at: http://127.0.0.1:8000

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Directory Structure
```bash
mkdir -p web/static/{css,js,images}
mkdir -p web/templates/reports
mkdir -p web/api
mkdir -p uploads logs
```

### 3. Download HTMX
```bash
# Download HTMX library
curl -o web/static/js/htmx.min.js https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js
```

### 4. Create Environment File
```bash
# Copy environment template
cp env.example .env
# Edit .env file with your settings
```

## Development Workflow

### Starting the Server
```bash
python run_web.py
```

### Features
- **Hot Reload**: Automatically restarts when code changes
- **Debug Mode**: Detailed error messages and logging
- **Development Tools**: Built-in debugging and profiling

### File Structure
```
ase-420-individual-project/
├── web/                    # Web application
│   ├── main.py            # FastAPI app entry point
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # Jinja2 templates
│   └── api/               # API endpoints
├── src/                   # Existing core logic (unchanged)
├── uploads/               # File upload directory
├── logs/                  # Application logs
├── .env                   # Environment configuration
└── requirements.txt       # Updated with web dependencies
```

## Configuration

### Environment Variables (.env file)
```bash
# Development settings
DEBUG=True
ENVIRONMENT=development

# Server configuration
HOST=127.0.0.1
PORT=8000
RELOAD=True

# File upload settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.txt,.md
UPLOAD_DIR=uploads

# Analysis settings
ANALYSIS_TIMEOUT=300  # 5 minutes
MAX_CONCURRENT_ANALYSES=5
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in .env file or run_web.py
   PORT=8001
   ```

2. **Dependencies not installed**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Permission errors**
   ```bash
   # Make sure you have write permissions
   chmod +x setup_web.py run_web.py
   ```

4. **HTMX not loading**
   ```bash
   # Manually download HTMX
   curl -o web/static/js/htmx.min.js https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js
   ```

### Getting Help

- Check the logs in the `logs/` directory
- Verify all dependencies are installed: `pip list`
- Test the setup: `python -c "import fastapi, uvicorn, jinja2"`

## Next Steps

After successful setup:
1. The web interface will be available at http://127.0.0.1:8000
2. You can start implementing the web features following the web_ui_plan.md
3. Use the development server for testing and development

## Production Deployment

For production deployment, you'll need to:
1. Set `DEBUG=False` in environment
2. Configure a production WSGI server (like Gunicorn)
3. Set up reverse proxy (like Nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

See the web_ui_plan.md for detailed implementation steps.
