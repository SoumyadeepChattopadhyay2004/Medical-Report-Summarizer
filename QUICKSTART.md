# 🚀 Quick Start Guide - Medical Report Summarizer

Get up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Grok API key from X.AI
- [ ] Tesseract OCR installed (for image processing)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd medical-report-summarizer
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Or use Chocolatey: `choco install tesseract`

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### 5. Configure API Key

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file and add your Grok API key:
```env
GROK_API_KEY=your_actual_api_key_here
```

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open automatically at: http://localhost:8501

## First Time Usage

### Step 1: Upload a Report
1. Click **"Upload Report"** in the sidebar
2. Choose a medical report file (PDF, JPG, PNG, or TXT)
3. Click **"Analyze Report"**

### Step 2: View Results
1. Wait for analysis to complete (10-30 seconds)
2. Click **"View Results"** to see the summary
3. Review:
   - Patient information
   - Executive summary
   - Risk assessment
   - Abnormal values
   - Health insights

### Step 3: Ask Questions
1. Navigate to **"Ask Questions"**
2. Type your question about the report
3. Get AI-powered answers

### Step 4: Export Report
1. Go to **"Export Report"**
2. Choose PDF or Text format
3. Download your analysis

## Testing with Sample Report

Try the included sample report:

```bash
# The sample report is located at:
examples/sample_report.txt
```

Upload this file to test all features without using your own medical reports.

## Common Issues & Solutions

### Issue: "Tesseract not found"
**Solution:**
```python
# Add to config.py if needed:
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: "API Key Error"
**Solution:**
- Verify your API key is correct
- Check `.env` file exists in the project root
- Ensure no extra spaces in the API key

### Issue: "Module not found"
**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "Port already in use"
**Solution:**
```bash
streamlit run app.py --server.port 8502
```

## Language Selection

- Use the **Language** dropdown in the sidebar
- Switch between English and Hindi
- Interface and insights will be translated

## Tips for Best Results

1. **File Quality**: Use clear, high-resolution images (300+ DPI)
2. **File Format**: PDF works best for text-based reports
3. **File Size**: Keep files under 10MB
4. **Report Format**: Standard medical lab reports work best

## Getting Help

- 📖 Read the full [README.md](README.md)
- 🏗️ Check [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)
- 🔧 Review [TECHNICAL_SPECIFICATIONS.md](TECHNICAL_SPECIFICATIONS.md)
- 💻 See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

## Next Steps

After getting started:

1. **Explore Features**: Try all pages and features
2. **Upload Your Reports**: Analyze your own medical reports
3. **Use the Chatbot**: Ask questions about your results
4. **Export Results**: Save your analysis for future reference
5. **Customize**: Modify settings in `config.py` as needed

## Security Reminder

⚠️ **Important**: 
- Never share your API key
- Your medical data is not stored
- All processing is session-based only
- Data is cleared when you close the browser

## Support

Need help? 
- Check the troubleshooting section in [README.md](README.md)
- Review the documentation files
- Open an issue on GitHub

---

**Ready to start?** Run `streamlit run app.py` and begin analyzing your medical reports! 🏥

**Disclaimer**: This tool is for informational purposes only. Always consult healthcare professionals for medical advice.