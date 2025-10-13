---
marp: true
size: 16:9
paginate: true
theme: default
---

<!-- _class: lead -->
# StressSpec Sprint 1 Review
## Requirements Stress Tester - Individual Project

**Individual Project – Jeffrey Perdue**  
**Sprint 1: MVP Implementation Complete**  
**October 15 2025**

---

## 🎯 Sprint 1 Demo

### **Working Features from Sprint 1**

- ✅ **Complete CLI Tool** - Full command-line interface with file processing
- ✅ **Web Application** - Modern FastAPI web interface with responsive design
- ✅ **6 Risk Detection Modules** - Ambiguity, Missing Detail, Security, Conflict, Performance, Availability
- ✅ **Multi-Format Reporting** - Markdown, CSV, JSON output formats
- ✅ **Configurable Rules System** - JSON-driven configuration with severity levels
- ✅ **Comprehensive Testing** - 59 passing tests (93.7% pass rate)

---

## 🖥️ Application Demo Screenshots


## 🌐 Web Application Demo

### **Modern Web Interface**
---

This is the landing page
![homepage.png](homepage.png)

---
We add a file
![homepage_post_upload.png](homepage_post_upload.png)

---
After selecting "Upload & Analyze" user is taken to Analysis Results page
![analysis_results.png](analysis_results.png)

---
**Key Features:**
- **File Upload System** - Drag-and-drop interface with validation
- **Real-time Analysis** - Background processing with progress tracking
- **Interactive Results** - Filtering, sorting, and detailed risk breakdown
- **Reports Dashboard** - Comprehensive reports management
- **Configuration Management** - Complete rules.json editing interface

---

## 📖 How to Use StressSpec

### **Getting Started**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jeffreyperdue/ase-420-individual-project
   cd StressSpec
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
---

### **Web Interface (Recommended)**

1. **Start the Web Server**
   ```bash
   python web/main.py
   ```

2. **Access the Application**
   - Open browser to `http://localhost:8000`
   - Upload a requirements file (.txt or .md)
   - Click "Upload & Analyze"
   - View results and download reports


---

## 📊 Sprint 1 Retrospective

### **Project Metrics**

| Metric | Count | Details |
|--------|-------|---------|
| **Lines of Code** | ~9,150 lines | Individual project codebase |
| **Features Implemented** | 6 major features | Complete MVP scope |
| **Requirements Delivered** | 7/7 (100%) | All original requirements met |
| **Burndown Rate** | 100% | (7/7) × 100% = 100% |
| **Test Coverage** | 59 passing tests | 93.7% pass rate |

---
| Metric | Count | Details |
|--------|-------|---------|
| **Risk Detectors** | 6 implemented | Ambiguity, Missing Detail, Security, Conflict, Performance, Availability |
| **Report Formats** | 3 formats | Markdown, CSV, JSON |
| **API Endpoints** | 25+ RESTful endpoints | Complete web API |

---

## 📈 What Went Well

### **✅ Successful Implementation Areas**

1. **Excellent Architecture** - Successfully implemented SOLID principles with Factory, Strategy, and Template Method patterns
2. **Comprehensive Testing** - 59 passing tests covering core functionality with 93.7% pass rate achieved
3. **Rapid MVP Delivery** - Completed full end-to-end workflow in Week 2, exceeding timeline expectations
4. **Web UI Excellence** - Delivered production-ready FastAPI web application with modern UI, responsive design, and comprehensive features
5. **Quality Code** - 9,150+ lines of well-structured, documented Python code following best practices

---
6. **Feature Expansion** - Implemented 6 risk detectors (vs. planned 4) plus complete web interface
7. **Production Readiness** - Delivered deployable web application with advanced features like reports dashboard and configuration management
8. **Test Infrastructure Success** - Resolved major async testing issues and achieved near-perfect test coverage

---

## ⚠️ What Went Wrong & Improvement Plan

### **Challenges Identified**

1. **Scope Creep** - Originally planned 4 risk detectors but implemented 6, plus added complete web UI which wasn't in original Sprint 1 scope
2. **Minor Integration Test Issues** - 4 remaining test failures in integration tests (93.7% pass rate achieved)
---
### **Analysis & Improvement Plan**

1. **Complete Test Coverage** - Address remaining 4 integration test failures to achieve 100% test pass rate
2. **Scope Management** - Better upfront planning to avoid feature creep, though the additional features were valuable
3. **Continuous Documentation** - Implement documentation-as-code approach with automated updates during development
4. **Performance Testing** - Add load testing for web application to ensure scalability under concurrent users

---

## 🎯 Sprint 2 Goals

### **Individual Sprint 2 Goals**

1. **Complete Test Coverage** - Address remaining 4 integration test failures to achieve 100% test pass rate
2. **Enhanced Risk Detection** - Add Privacy, Traceability, and Scope detection modules (completing original 8-category plan)
3. **Enhanced Reporting** - Implement basic HTML reports with professional styling
4. **Advanced Scoring** - Implement "Top 5 Riskiest Requirements" analysis and enhanced severity scoring

---

## 📋 Sprint 2 Project Metrics

### **Individual Sprint 2 Metrics (Realistic)**

| Feature | Requirements | Timeline |
|---------|--------------|----------|
| **Complete Test Coverage** | Fix 4 integration test failures | Week 6 |
| **Privacy Detector** | GDPR/CCPA compliance checks | Week 6 |
| **Traceability Detector** | Requirement ID validation | Week 7 |
| **Scope Detector** | Scope creep detection | Week 7 |
| **Top 5 Riskiest Analysis** | Combined risk scoring | Week 8 |
| **HTML Report Generation** | Professional styling | Week 9 |
| **Documentation Updates** | User guides and examples | Week 10 |

**Number of individual features planned: 4**  
**Number of individual requirements planned: 6**

---

## 🗓️ Updated Timeline and Milestones

### **Updated Individual Timeline and Milestones**

- **Week 6**: Complete test coverage + Privacy detector (100% test pass rate + 1 new risk detector)
- **Week 7**: Traceability detector + Scope detector (complete 8-category risk detection system)
- **Week 8**: Enhanced severity scoring + "Top 5 Riskiest Requirements" analysis (advanced scoring features)
- **Week 9**: Basic HTML reports with Bootstrap styling (professional report generation)
- **Week 10**: Testing, bug fixes, and documentation updates (polish and finalize Sprint 2 features)

### **Sprint 2 Success Criteria**

- ✅ All 8 risk detection categories implemented and tested
- ✅ 100% test pass rate achieved
- ✅ "Top 5 Riskiest Requirements" analysis functional
- ✅ Standalone HTML report generation working
- ✅ All existing functionality preserved and enhanced

---

## 🏆 Sprint 1 Achievements

### **MVP Status: Complete ✅**

**Delivered Beyond Original Scope:**
- ✅ **CLI Tool** - Complete command-line interface
- ✅ **Web Application** - Full-featured web interface
- ✅ **6 Risk Detectors** - Comprehensive risk detection
- ✅ **Multi-Format Reports** - Markdown, CSV, JSON
- ✅ **Configuration System** - JSON-driven rules
- ✅ **Production Quality** - Error handling, security, performance

### **Ready for Sprint 2**

The foundation is solid with modern architecture, comprehensive features, and production-quality implementation. Sprint 2 will complete the original 8-category vision and add advanced reporting capabilities.

---

## 📊 Sprint 1 Summary Statistics

| Category | Metric | Count | Status |
|----------|--------|-------|--------|
| **Code** | Lines of Code | ~9,150 | ✅ Complete |
| **Features** | Major Features | 6 | ✅ Complete |
| **Requirements** | User Stories | 7/7 (100%) | ✅ Complete |
| **Burndown** | Completion Rate | 100% | ✅ Complete |
| **Testing** | Test Files | 7 | ✅ Complete |
| **Testing** | Passing Tests | 59 | 🔄 93.7% |
| **Detectors** | Risk Categories | 6/8 | 🔄 75% |
| **Reports** | Output Formats | 3 | ✅ Complete |

**Overall Sprint 1 Completion: 100% ✅**

---

## 📝 Individual Progress Summary

### **Sprint 1 Weekly Breakdown**

- **Week 1**: Project setup, architecture design, and initial CLI foundation. Created basic project structure with file loader and requirement parser modules.

- **Week 2**: **MVP COMPLETE** - Delivered full end-to-end workflow with 800+ lines of code, 27 passing tests, and comprehensive CLI interface. Exceeded timeline by completing core functionality ahead of schedule.

- **Week 3**: Enhanced risk detection with 6 detector modules, implemented multi-format reporting (Markdown, CSV, JSON), and added configurable rules system. Total of 42 passing tests with robust architecture.

- **Week 4**: **WEB UI COMPLETE** - Delivered production-ready FastAPI web application with modern UI, responsive design, file upload system, real-time analysis, and comprehensive API. Final codebase: 9,154+ lines across 50+ Python files with complete web interface exceeding original Sprint 1 scope.

