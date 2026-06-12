# 🏥 Medical Report Summarizer

A comprehensive AI-powered medical report analysis tool that helps users understand their medical reports through intelligent summarization, abnormal value detection, risk assessment, and personalized health insights.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

### 1. **Medical Report Summarization**
- Comprehensive AI-powered report analysis
- Key findings extraction
- Structured summary generation
- Executive summary for quick overview

### 2. **Abnormal Value Detection**
- Automatic comparison with normal ranges
- Severity classification (Normal, Borderline, Abnormal, Critical)
- Color-coded highlighting
- Detailed deviation analysis

### 3. **Medical Terminology Simplification**
- Converts medical jargon to layman terms
- Context-aware explanations
- Interactive glossary
- Common abbreviations dictionary

### 4. **Risk Assessment with Explainable AI**
- Comprehensive health risk scoring (0-100)
- Risk level classification (Low, Moderate, High, Critical)
- Explainable AI with factor breakdown
- Visual risk gauge

### 5. **Personalized Health Insights**
- Lifestyle recommendations
- Dietary guidance
- Exercise suggestions
- Monitoring plans
- Preventive measures

### 6. **AI-Powered Chatbot**
- Context-aware Q&A
- Medical report-specific responses
- Follow-up question suggestions
- Conversation history

### 7. **Multilingual Support**
- English and Hindi interfaces
- Real-time translation
- Language-specific medical terms

### 8. **Additional Features**
- Multiple file format support (PDF, Images, Text)
- OCR for scanned documents
- Export to PDF and Text
- Data visualization with charts
- Responsive design

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
- **Tesseract OCR** (for image processing)
- **Grok API Key** from X.AI

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd medical-report-summarizer
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Tesseract OCR

#### Windows:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Or use Chocolatey: `choco install tesseract`

#### macOS:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Step 5: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Grok API key:
```env
GROK_API_KEY=your_actual_grok_api_key_here
GROK_API_BASE=https://api.x.ai/v1
GROK_MODEL=grok-beta
```

### Step 6: Verify Installation

```bash
python -c "import streamlit; import pytesseract; print('All dependencies installed successfully!')"
```

## 🎯 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Using the Application

1. **Upload Report**
   - Click on "Upload Report" in the sidebar
   - Select your medical report (PDF, JPG, PNG, or TXT)
   - Click "Analyze Report"

2. **View Summary**
   - Review patient information
   - Read executive summary
   - Check risk assessment
   - View abnormal values
   - Explore health insights

3. **Ask Questions**
   - Navigate to "Ask Questions"
   - Type your question about the report
   - Get AI-powered responses
   - Use suggested questions

4. **Export Report**
   - Go to "Export Report"
   - Choose PDF or Text format
   - Download your analysis

### Language Selection

- Use the language selector in the sidebar
- Switch between English and Hindi
- Interface and insights will be translated

## 📁 Project Structure

```
medical-report-summarizer/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore file
├── README.md                       # This file
├── PROJECT_ARCHITECTURE.md         # System architecture
├── TECHNICAL_SPECIFICATIONS.md     # Technical details
├── IMPLEMENTATION_GUIDE.md         # Development guide
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── grok_client.py             # Grok API integration
│   ├── file_processor.py          # File processing
│   ├── medical_analyzer.py        # Medical analysis
│   ├── translator.py              # Translation support
│   └── export_handler.py          # Export functionality
│
├── modules/                        # Analysis modules
│   ├── __init__.py
│   ├── summarizer.py              # Report summarization
│   ├── abnormal_detector.py      # Abnormal value detection
│   ├── terminology.py             # Term simplification
│   ├── risk_assessor.py           # Risk assessment
│   ├── insights_generator.py     # Health insights
│   └── chatbot.py                 # Chatbot logic
│
├── assets/                         # Static assets
│   ├── medical_ranges.json        # Normal value ranges
│   └── styles.css                 # Custom CSS (optional)
│
├── examples/                       # Example reports
│   ├── sample_report.pdf
│   ├── sample_report.txt
│   └── sample_report.jpg
│
└── docs/                          # Documentation
    └── API_DOCUMENTATION.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROK_API_KEY` | Your Grok API key | Required |
| `GROK_API_BASE` | Grok API endpoint | https://api.x.ai/v1 |
| `GROK_MODEL` | Model to use | grok-beta |
| `MAX_FILE_SIZE` | Max upload size (bytes) | 10485760 (10MB) |
| `DEFAULT_LANGUAGE` | Default language | en |
| `LOG_LEVEL` | Logging level | INFO |

### Customization

Edit `config.py` to customize:
- Color schemes
- Risk thresholds
- AI parameters
- Feature flags

## 📊 Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | .pdf | Text-based and scanned |
| Images | .jpg, .jpeg, .png, .tiff | OCR processing |
| Text | .txt | Plain text reports |

## 🔒 Security & Privacy

- **No Data Storage**: All data is session-based only
- **API Key Security**: Keys stored in environment variables
- **File Validation**: Strict file type and size checks
- **No Third-Party Sharing**: Your data stays private

## ⚠️ Important Disclaimers

1. **Not Medical Advice**: This tool is for informational purposes only
2. **Consult Professionals**: Always consult healthcare providers for medical decisions
3. **AI Limitations**: AI-generated content may contain errors
4. **Emergency Situations**: Seek immediate medical attention for emergencies

## 🐛 Troubleshooting

### Common Issues

**1. Tesseract Not Found**
```bash
# Windows: Add Tesseract to PATH
# Or specify path in code:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**2. API Key Error**
- Verify your Grok API key is correct
- Check `.env` file exists and is properly formatted
- Ensure no extra spaces in the API key

**3. Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**4. OCR Not Working**
- Ensure Tesseract is installed
- Check image quality (minimum 300 DPI recommended)
- Try converting PDF to images first

**5. Memory Issues**
- Reduce file size
- Close other applications
- Increase system memory allocation

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=. tests/
```

### Code Style

```bash
# Install formatting tools
pip install black flake8

# Format code
black .

# Check style
flake8 .
```

## 📚 Documentation

- [Project Architecture](PROJECT_ARCHITECTURE.md)
- [Technical Specifications](TECHNICAL_SPECIFICATIONS.md)
- [Implementation Guide](IMPLEMENTATION_GUIDE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)

## 🔄 Version History

### Version 1.0.0 (Current)
- Initial release
- Core features implemented
- English and Hindi support
- PDF, Image, and Text processing
- Risk assessment with explainable AI
- Interactive chatbot
- Export functionality

## 🗺️ Roadmap

### Planned Features
- [ ] Additional language support (Spanish, French, German)
- [ ] Mobile application
- [ ] Integration with EHR systems
- [ ] Wearable device connectivity
- [ ] Advanced data visualization
- [ ] Report comparison over time
- [ ] Voice input support
- [ ] Telemedicine integration

## 📧 Support

For support, please:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [Documentation](#-documentation)
3. Open an issue on GitHub
4. Contact: support@example.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Grok AI** by X.AI for powerful language model
- **Streamlit** for the amazing web framework
- **Tesseract OCR** for text extraction
- **OpenAI** for API compatibility
- All contributors and users

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for better healthcare understanding**

**Disclaimer**: This tool is for educational and informational purposes only. It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.