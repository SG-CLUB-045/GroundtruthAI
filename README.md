# H001 - Automated Insight Engine 🚀

Transform raw data into comprehensive, executive-ready business intelligence reports with AI-powered strategic insights. Generate actionable recommendations, SWOT analysis, and competitive intelligence in minutes.

## 🎯 Overview

It is an advanced business intelligence platform that automatically analyzes your data and generates strategic reports with:

- **Advanced Business Analytics**: KPIs, ROI, profit margins, growth metrics
- **Strategic Frameworks**: SWOT analysis, growth opportunities, risk assessment
- **AI-Powered Insights**: Google Gemini-powered strategic recommendations
- **Professional Reports**: Executive-ready PDF and PowerPoint presentations
- **Web Interface**: Easy-to-use dashboard for data upload and report generation

## ✨ Key Features

### Business Intelligence
- ✅ **Automatic KPI Calculation**: Revenue, profit, ROI, conversion rates, market share
- ✅ **SWOT Analysis**: Automated strengths, weaknesses, opportunities, threats identification
- ✅ **Growth Opportunities**: High-impact opportunities with impact/effort analysis
- ✅ **Risk Assessment**: Volatility analysis and threat detection
- ✅ **Strategic Recommendations**: Prioritized action items with timelines

### Data Analysis
- ✅ **Statistical Analysis**: Mean, median, std dev, min/max for all numeric columns
- ✅ **Trend Analysis**: Daily, weekly, monthly trend detection
- ✅ **Correlation Analysis**: Pearson correlation between metrics
- ✅ **Data Visualization**: Automatic chart generation (bar, line, pie, scatter)

### AI Integration
- ✅ **Google Gemini Integration**: Strategic business insights generation
- ✅ **Executive Summaries**: Board-level strategic summaries
- ✅ **Key Findings**: Data-driven strategic discoveries
- ✅ **Actionable Recommendations**: Prioritized strategic actions

### Report Generation
- ✅ **PDF Reports**: Comprehensive business intelligence reports
- ✅ **PowerPoint Presentations**: Executive-ready slide decks
- ✅ **Professional Styling**: Branded, publication-ready formatting
- ✅ **Multiple Visualizations**: Charts and tables embedded in reports


## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment (Optional)

Create a `.env` file for AI insights:

```bash

GEMINI_API_KEY=your_gemini_api_key_here
```


**Note**: The application works without an API key but will use fallback mode for insights.

### 3. Run the Application

```bash
python main.py
```

Open your browser to: **http://localhost:5000**

### 4. Generate Your First Report

1. Upload a CSV or JSON file
2. Select report format (PDF, PowerPoint, or Both)
3. (Optional) Add business context
4. Click "Generate Report"
5. Download your strategic business intelligence report!


## 💻 Usage

### Web Interface

The easiest way to use GroundtruthAI is through the web interface:

1. Start the server: `python main.py`
2. Open http://localhost:5000
3. Upload your data file
4. Generate and download reports

## 📊 What's Included in Reports

### Business Intelligence Sections

1. **Executive Summary**
   - Strategic overview
   - Key performance highlights
   - Business implications

2. **Business KPIs**
   - Total revenue and growth
   - Profit margins and ROI
   - Conversion rates
   - Revenue per customer
   - Cost efficiency metrics

3. **SWOT Analysis**
   - Strengths: High-performing metrics
   - Weaknesses: Underperforming areas
   - Opportunities: Growth potential
   - Threats: Declining trends

4. **Growth Opportunities**
   - High-impact, low-effort opportunities
   - Segment performance analysis
   - Scaling recommendations

5. **Risk Assessment**
   - High-risk factors
   - Volatility analysis
   - Threat mitigation strategies

6. **Strategic Recommendations**
   - Prioritized action items (P0, P1)
   - Expected impact and timelines
   - Implementation complexity

7. **Data Visualizations**
   - Distribution charts
   - Trend analysis charts
   - Top performers visualization

8. **Statistical Tables**
   - Comprehensive metrics tables
   - Correlation matrices
   - Performance summaries


## 📦 Dependencies

- **pandas**: Data processing and analysis
- **matplotlib**: Data visualization
- **reportlab**: PDF generation
- **python-pptx**: PowerPoint generation
- **google-generativeai**: AI insights (Gemini)
- **flask**: Web server
- **flask-cors**: CORS support
- **Pillow**: Image processing
- **openpyxl**: Excel file support
- **python-dotenv**: Environment variables

## 🎓 Example Use Cases

### Marketing Performance Analysis
- Analyze campaign performance data
- Identify top-performing campaigns
- Calculate ROI and conversion rates
- Generate strategic recommendations

### Sales Analytics
- Revenue trend analysis
- Customer segmentation insights
- Growth opportunity identification
- Risk factor assessment

### Financial Analysis
- Profit margin optimization
- Cost efficiency analysis
- Revenue growth forecasting
- Strategic financial recommendations

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
# Google Gemini API (Optional but recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
```

### File Size Limits

- Maximum file size: 100MB
- Recommended: < 50MB for optimal performance
- Processing time: 5-60 seconds depending on file size

## 🐛 Troubleshooting

### Gemini API Key Issues
```
Error: No Gemini API key provided
Solution: Set GEMINI_API_KEY environment variable or use fallback mode
```

### File Upload Errors
```
Error: File too large
Solution: Files must be under 100MB. Split large files or sample data
```

### Port Already in Use
```
Error: Port 5000 already in use
Solution: Change port in main.py or stop the process using port 5000
```

### Import Errors
```
Error: Module not found
Solution: Ensure virtual environment is activated and dependencies installed
```


## 📝 Sample Data

The project includes sample datasets under:

- `sample_data/


## 🎯 What Makes This Different

Unlike generic data analysis tools, It Provides:

1. **Strategic Business Intelligence**: Not just statistics, but actionable business insights
2. **Automated SWOT Analysis**: Strategic framework generation
3. **Prioritized Recommendations**: Impact-based action prioritization
4. **Competitive Intelligence**: Market share and positioning analysis
5. **Risk Assessment**: Proactive threat identification
6. **Executive-Ready Reports**: Content to Increase presentation quality
