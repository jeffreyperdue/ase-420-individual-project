# StressSpec Web UI - Quick Start Guide

## 🚀 **How to Run the Web Application**

### **Prerequisites**
- Python 3.8 or higher
- All dependencies installed (run `python setup_web.py` if not done already)

### **Method 1: Development Server (Recommended)**

```bash
# Navigate to the project directory
cd StressSpec

# Start the development server
python run_web.py
```

### **Method 2: Direct FastAPI**

```bash
# Navigate to the project directory
cd StressSpec

# Run FastAPI directly
python -m uvicorn web.main:app --host 127.0.0.1 --port 8000 --reload
```

### **Method 3: Using the Main App**

```bash
# Navigate to the project directory
cd StressSpec

# Run the main FastAPI app
python web/main.py
```

## 🌐 **Accessing the Application**

Once the server is running, you can access:

- **Main Web Interface**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/api/docs
- **Alternative API Docs**: http://127.0.0.1:8000/api/redoc
- **Health Check**: http://127.0.0.1:8000/health

## 📁 **What You'll See**

### **Main Page (http://127.0.0.1:8000)**
- File upload interface for .txt and .md files
- Real-time analysis progress
- Interactive results display
- Sample file downloads

### **API Endpoints**
- `POST /api/upload/` - Upload requirement files
- `POST /api/analysis/start` - Start analysis
- `GET /api/analysis/status/{analysis_id}` - Check analysis progress
- `GET /api/analysis/results/{analysis_id}` - Get analysis results
- `POST /api/reports/generate` - Generate reports
- `GET /api/reports/download/{report_id}` - Download reports

## 🧪 **Testing the Application**

### **1. Upload a Sample File**
- Download the sample files from the main page
- Upload a .txt or .md file with requirements
- Watch the real-time analysis progress

### **2. Test the API**
- Visit http://127.0.0.1:8000/api/docs
- Try the interactive API documentation
- Test file upload and analysis endpoints

### **3. Check Analysis Results**
- View the interactive results page
- Filter risks by severity and category
- Download reports in multiple formats

## 🔧 **Development Features**

### **Hot Reload**
- The development server automatically reloads when you change code
- No need to restart the server for most changes

### **Debug Mode**
- Detailed error messages in the browser
- Console logging for troubleshooting
- Automatic API documentation updates

### **File Monitoring**
- The server watches the `web/` directory for changes
- Static files are served automatically
- Templates are reloaded on changes

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Change port in .env file or run_web.py
   PORT=8001
   ```

2. **Dependencies Not Installed**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Permission Errors**
   ```bash
   # Make sure you have write permissions
   chmod +x run_web.py
   ```

4. **Module Import Errors**
   ```bash
   # Check if you're in the right directory
   pwd
   # Should show: .../ase-420-individual-project
   ```

### **Getting Help**

- Check the logs in the `logs/` directory
- Verify all dependencies: `pip list`
- Test the setup: `python -c "import fastapi, uvicorn, jinja2"`

## 📊 **Current Status**

### ✅ **Completed Features**
- FastAPI application with routing and middleware
- File upload system with validation
- Analysis processing with background tasks
- Report generation in multiple formats
- Responsive web interface with Bootstrap 5
- HTMX integration for dynamic interactions
- Error handling and user feedback

### 🔄 **In Development**
- Real-time analysis progress updates
- Interactive risk filtering and sorting
- Configuration management interface
- Advanced reporting features

## 🎯 **Next Steps**

1. **Test the Application**: Upload sample files and run analysis
2. **Explore the API**: Use the interactive documentation
3. **Customize**: Modify templates and styling as needed
4. **Deploy**: Set up production deployment when ready

## 📚 **Additional Resources**

- **Setup Guide**: See `WEB_SETUP.md` for detailed setup instructions
- **Implementation Plan**: See `Sprint2_Features_and_Plan.md` for development roadmap
- **API Documentation**: Available at `/api/docs` when server is running
- **Sample Files**: Download from the main page to test the application

---

**Happy coding! 🚀**
