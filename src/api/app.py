"""
Flask API Server for Automated Insight Engine
Handles data upload, processing, report generation, and download
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import pandas as pd

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS

from src.data_ingestion import DataIngester
from src.analysis import DataAnalyzer
from src.analysis.business_analyzer import BusinessAnalyzer
from src.llm import InsightGenerator
from src.reporting import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def allowed_file(filename):
    """Check if file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app(config=None):
    """
    Application factory for creating Flask app.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    CORS(app)
    
    if config is None:
        config = {}
    
    project_root = Path(__file__).parent.parent.parent.resolve()
    
    upload_folder = config.get('upload_folder', './uploads')
    output_folder = config.get('output_folder', './output')
    
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(project_root, upload_folder.lstrip('./'))
    if not os.path.isabs(output_folder):
        output_folder = os.path.join(project_root, output_folder.lstrip('./'))
    
    app.config.update(
        UPLOAD_FOLDER=os.path.abspath(upload_folder),
        OUTPUT_FOLDER=os.path.abspath(output_folder),
        MAX_CONTENT_LENGTH=MAX_FILE_SIZE,
        JSON_SORT_KEYS=False
    )
    
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        os.makedirs(folder, exist_ok=True)
    
    app.processing_jobs = {}
    
    @app.route('/', methods=['GET'])
    def index():
        """Serve HTML interface."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Automated Insight Engine</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .container {
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 900px;
                    width: 100%;
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }
                .header h1 { font-size: 2.5em; margin-bottom: 10px; }
                .header p { font-size: 1.1em; opacity: 0.9; }
                .content {
                    padding: 40px;
                }
                .form-group {
                    margin-bottom: 25px;
                }
                label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                    color: #333;
                }
                input, select, textarea {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    font-size: 1em;
                    transition: border-color 0.3s;
                }
                input:focus, select:focus, textarea:focus {
                    outline: none;
                    border-color: #2E86AB;
                    box-shadow: 0 0 0 3px rgba(46,134,171,0.1);
                }
                button {
                    background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                    color: white;
                    padding: 14px 30px;
                    border: none;
                    border-radius: 6px;
                    font-size: 1.1em;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 20px rgba(46,134,171,0.3);
                }
                button:active {
                    transform: translateY(0);
                }
                .api-docs {
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 6px;
                    margin-top: 40px;
                    border-left: 4px solid #2E86AB;
                }
                .api-docs h3 { margin-bottom: 15px; color: #2E86AB; }
                .endpoint {
                    background: white;
                    padding: 12px;
                    margin: 10px 0;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }
                .success { color: #4CAF50; }
                .error { color: #f44336; }
                .info { color: #2196F3; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Automated Insight Engine</h1>
                    <p>Transform Data into Executive Insights</p>
                </div>
                <div class="content">
                    <form id="uploadForm">
                        <div class="form-group">
                            <label for="file">📁 Upload CSV/JSON File</label>
                            <input type="file" id="file" name="file" accept=".csv,.json,.xlsx" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="reportType">📊 Report Format</label>
                            <select id="reportType" name="reportType">
                                <option value="pdf">PDF Report</option>
                                <option value="pptx">PowerPoint Presentation</option>
                                <option value="both">Both PDF & PPTX</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="context">💡 Business Context (Optional)</label>
                            <textarea id="context" name="context" placeholder="Describe your data and business goals..." rows="3"></textarea>
                        </div>
                        
                        <div class="form-group">
                            <button type="submit">Generate Report ✨</button>
                        </div>
                    </form>
                    
                    <div id="status" style="margin-top: 20px; display: none;"></div>
                </div>
            </div>
            
            <script>
                document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const file = document.getElementById('file').files[0];
                    const reportType = document.getElementById('reportType').value;
                    const context = document.getElementById('context').value;
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('reportType', reportType);
                    formData.append('context', context);
                    
                    const statusDiv = document.getElementById('status');
                    statusDiv.style.display = 'block';
                    statusDiv.innerHTML = '<p class="info">⏳ Processing... This may take a minute.</p>';
                    
                    try {
                        const response = await fetch('/api/process', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        
                        if (response.ok) {
                            let html = '<p class="success">✅ Report generated successfully!</p>';
                            html += '<p><strong>Download your reports:</strong></p>';
                            
                            if (data.reports.pdf) {
                                html += `<p><a href="${data.reports.pdf}" target="_blank" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #2E86AB; color: white; text-decoration: none; border-radius: 5px;">📄 Download PDF</a></p>`;
                            }
                            if (data.reports.pptx) {
                                html += `<p><a href="${data.reports.pptx}" target="_blank" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #A23B72; color: white; text-decoration: none; border-radius: 5px;">🎯 Download PowerPoint</a></p>`;
                            }
                            
                            statusDiv.innerHTML = html;
                        } else {
                            statusDiv.innerHTML = `<p class="error">❌ Error: ${data.error}</p>`;
                        }
                    } catch (error) {
                        statusDiv.innerHTML = `<p class="error">❌ Error: ${error.message}</p>`;
                    }
                });
            </script>
        </body>
        </html>
        """
        return render_template_string(html)

    @app.route('/api/process', methods=['POST'])
    def process_data():
        """Process uploaded file and generate reports."""
        try:
            # Check if file is present
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400
            
            report_type = request.form.get('reportType', 'pdf')
            context = request.form.get('context', '')
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logger.info(f"Processing file: {filename}")
            
            ingester = DataIngester(use_polars=False)
            analyzer = DataAnalyzer()
            business_analyzer = BusinessAnalyzer()
            
            try:
                insight_gen = InsightGenerator()
                if not insight_gen.is_available():
                    return jsonify({
                        "error": "Gemini API is required to generate detailed reports. Please set GEMINI_API_KEY environment variable."
                    }), 400
            except (ValueError, ImportError) as e:
                return jsonify({
                    "error": f"Gemini API initialization failed: {str(e)}. Detailed reports can only be generated through Gemini AI."
                }), 400
            
            report_gen = ReportGenerator(app.config['OUTPUT_FOLDER'])
            
            if filename.endswith('.csv'):
                data = ingester.from_csv(filepath)
            elif filename.endswith('.json'):
                data = ingester.from_json(filepath)
            elif filename.endswith('.xlsx'):
                data = pd.read_excel(filepath)
            
            ingester.clean_data(data)
            analyzer.load_data(data)
            business_analyzer.load_data(data)
            
            stats = analyzer.calculate_basic_statistics()
            summary = analyzer.get_summary_insights()
            
            business_kpis = business_analyzer.calculate_business_kpis()
            swot_analysis = business_analyzer.generate_swot_analysis(context)
            growth_opportunities = business_analyzer.identify_growth_opportunities()
            risk_factors = business_analyzer.calculate_risk_factors()
            strategic_recommendations = business_analyzer.generate_strategic_recommendations()
            
            all_metrics = analyzer.get_metrics()
            all_metrics['business_kpis'] = business_kpis
            all_metrics['swot_analysis'] = swot_analysis
            all_metrics['growth_opportunities'] = growth_opportunities
            all_metrics['risk_factors'] = risk_factors
            all_metrics['strategic_recommendations'] = strategic_recommendations
            
            trends = None
            date_cols = [col for col in data.columns if 'date' in col.lower() or 'time' in col.lower()]
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            
            if date_cols and numeric_cols:
                try:
                    trends = analyzer.calculate_trends(
                        date_column=date_cols[0],
                        value_column=numeric_cols[0],
                        period='daily'
                    )
                except:
                    pass
            
            correlations = None
            if len(numeric_cols) > 1:
                try:
                    correlations = analyzer.calculate_correlations()
                except:
                    pass
            
            try:
                narrative = insight_gen.generate_insight_narrative(
                    all_metrics,
                    title="Strategic Business Intelligence Report",
                    detailed=True
                )
            except ValueError as e:
                logger.error(f"Failed to generate insights with Gemini: {str(e)}")
                return jsonify({
                    "error": f"Failed to generate detailed report: {str(e)}. Please ensure GEMINI_API_KEY is set correctly."
                }), 500
            
            chart_paths = []
            
            if numeric_cols:
                col = numeric_cols[0]
                if len(data[col].unique()) <= 20:
                    chart_data = data[col].value_counts().to_dict()
                    chart_path = report_gen.create_chart(
                        chart_data,
                        chart_type="bar",
                        title=f"Distribution of {col}",
                        ylabel="Count",
                        xlabel=col
                    )
                    if chart_path:
                        chart_paths.append(chart_path)
            
            categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols and numeric_cols:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                try:
                    top_values = data.groupby(cat_col)[num_col].sum().nlargest(10).to_dict()
                    chart_path = report_gen.create_chart(
                        top_values,
                        chart_type="bar",
                        title=f"Top 10 {cat_col} by {num_col}",
                        ylabel=num_col,
                        xlabel=cat_col
                    )
                    if chart_path:
                        chart_paths.append(chart_path)
                except:
                    pass
            
            if trends and date_cols and numeric_cols:
                try:
                    trend_data = trends.get('trend_data', {})
                    if isinstance(trend_data, dict) and 'sum' in str(trend_data):
                        trend_values = {}
                        for key, value in list(trend_data.items())[:20]:  # Limit to 20 points
                            if isinstance(value, dict) and 'sum' in value:
                                trend_values[str(key)] = value['sum']
                            elif isinstance(value, (int, float)):
                                trend_values[str(key)] = value
                        
                        if trend_values:
                            chart_path = report_gen.create_chart(
                                trend_values,
                                chart_type="line",
                                title=f"Trend Analysis: {numeric_cols[0]} over Time",
                                ylabel=numeric_cols[0],
                                xlabel=date_cols[0]
                            )
                            if chart_path:
                                chart_paths.append(chart_path)
                except Exception as e:
                    logger.warning(f"Could not create trend chart: {str(e)}")
            
            exec_summary = narrative.get("executive_summary", 
                f"This report analyzes {summary['total_rows']} records across {summary['total_columns']} dimensions. "
                f"The analysis reveals key patterns and insights to inform strategic decision-making.")
            
            # Build comprehensive business sections
            sections = {
                "Executive Summary": exec_summary,
                "Data Overview": (
                    f"This strategic analysis is based on {summary['total_rows']:,} records with {summary['total_columns']} data columns.\n\n"
                    f"Dataset Structure:\n"
                    f"• Total Records: {summary['total_rows']:,}\n"
                    f"• Total Columns: {summary['total_columns']}\n"
                    f"• Numeric Columns: {len(numeric_cols)}\n"
                    f"• Categorical Columns: {len(categorical_cols)}\n"
                    f"• Data Quality: {((summary['total_rows'] - data.isna().sum().sum()) / (summary['total_rows'] * summary['total_columns']) * 100):.1f}% complete"
                ),
            }
            
            if business_kpis:
                kpi_text = "Key Business Performance Indicators:\n\n"
                if 'total_revenue' in business_kpis:
                    kpi_text += f"💰 Total Revenue: ${business_kpis['total_revenue']:,.2f}\n"
                if 'profit_margin' in business_kpis:
                    kpi_text += f"📊 Profit Margin: {business_kpis['profit_margin']:.2f}%\n"
                if 'roi' in business_kpis:
                    kpi_text += f"📈 ROI: {business_kpis['roi']:.2f}%\n"
                if 'revenue_growth' in business_kpis and business_kpis['revenue_growth']:
                    kpi_text += f"🚀 Revenue Growth: {business_kpis['revenue_growth']:.2f}%\n"
                if 'conversion_rate' in business_kpis:
                    kpi_text += f"🎯 Conversion Rate: {business_kpis['conversion_rate']:.2f}%\n"
                if 'revenue_per_customer' in business_kpis:
                    kpi_text += f"👥 Revenue per Customer: ${business_kpis['revenue_per_customer']:,.2f}\n"
                sections["Business KPIs"] = kpi_text
            
            if swot_analysis:
                swot_text = "Strategic SWOT Analysis:\n\n"
                swot_text += "💪 Strengths:\n"
                for strength in swot_analysis.get('strengths', [])[:5]:
                    swot_text += f"  • {strength}\n"
                swot_text += "\n⚠️ Weaknesses:\n"
                for weakness in swot_analysis.get('weaknesses', [])[:5]:
                    swot_text += f"  • {weakness}\n"
                swot_text += "\n🎯 Opportunities:\n"
                for opp in swot_analysis.get('opportunities', [])[:5]:
                    swot_text += f"  • {opp}\n"
                swot_text += "\n⚠️ Threats:\n"
                for threat in swot_analysis.get('threats', [])[:5]:
                    swot_text += f"  • {threat}\n"
                sections["SWOT Analysis"] = swot_text
            
            if growth_opportunities:
                opp_text = "Identified Growth Opportunities:\n\n"
                for idx, opp in enumerate(growth_opportunities[:5], 1):
                    opp_text += f"{idx}. {opp.get('segment', 'Segment')} - {opp.get('metric', 'Metric')}\n"
                    opp_text += f"   Current Value: {opp.get('current_value', 0):,.2f}\n"
                    opp_text += f"   Potential: {opp.get('potential', 'N/A')}\n"
                    opp_text += f"   Impact: {opp.get('impact', 'N/A')} | Effort: {opp.get('effort', 'N/A')}\n\n"
                sections["Growth Opportunities"] = opp_text
            
            if risk_factors:
                risk_text = "Business Risk Assessment:\n\n"
                if risk_factors.get('high_risk'):
                    risk_text += "🔴 High Risk Factors:\n"
                    for risk in risk_factors['high_risk'][:3]:
                        risk_text += f"  • {risk.get('metric', 'Metric')}: {risk.get('issue', 'Issue')}\n"
                        if 'recommendation' in risk:
                            risk_text += f"    Recommendation: {risk['recommendation']}\n"
                    risk_text += "\n"
                if risk_factors.get('medium_risk'):
                    risk_text += "🟡 Medium Risk Factors:\n"
                    for risk in risk_factors['medium_risk'][:3]:
                        risk_text += f"  • {risk.get('metric', 'Metric')}: {risk.get('issue', 'Issue')}\n"
                sections["Risk Analysis"] = risk_text
            
            if stats:
                metrics_text = "Key Performance Metrics:\n\n"
                for col, stat in list(stats.items())[:5]:
                    metrics_text += f"{col}:\n"
                    metrics_text += f"  • Mean: {stat.get('mean', 0):,.2f}\n"
                    metrics_text += f"  • Median: {stat.get('median', 0):,.2f}\n"
                    metrics_text += f"  • Range: {stat.get('min', 0):,.2f} - {stat.get('max', 0):,.2f}\n"
                    metrics_text += f"  • Standard Deviation: {stat.get('std', 0):,.2f}\n\n"
                sections["Key Metrics"] = metrics_text
            
            if trends:
                trend_dir = trends.get('trend_direction', 'stable')
                sections["Trend Analysis"] = (
                    f"Analysis of {trends.get('period', 'daily')} trends shows a {trend_dir} pattern. "
                    f"This indicates the data is {'growing' if trend_dir == 'increasing' else 'declining' if trend_dir == 'decreasing' else 'stable'} over the analyzed period."
                )
            
            tables = []
            if stats:
                stats_table_data = [["Metric", "Mean", "Median", "Min", "Max", "Std Dev"]]
                for col, stat in list(stats.items())[:10]:
                    stats_table_data.append([
                        col[:30],
                        f"{stat.get('mean', 0):,.2f}",
                        f"{stat.get('median', 0):,.2f}",
                        f"{stat.get('min', 0):,.2f}",
                        f"{stat.get('max', 0):,.2f}",
                        f"{stat.get('std', 0):,.2f}"
                    ])
                tables.append({
                    "title": "Statistical Summary",
                    "data": stats_table_data
                })
            
            report_paths = {}
            job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if report_type in ['pdf', 'both']:
                try:
                    pdf_path = report_gen.generate_pdf_report(
                        title="Strategic Business Intelligence Report",
                        subtitle=f"Advanced Analytics & Competitive Insights - {filename}",
                        sections=sections,
                        tables=tables,
                        charts=chart_paths,
                        insights={
                            "Key Findings": narrative.get("key_findings", []),
                            "Recommendations": narrative.get("recommendations", []),
                            "Executive Summary": narrative.get("executive_summary", ""),
                            "Strategic Recommendations": [f"{r.get('priority', '')}: {r.get('action', '')}" for r in strategic_recommendations[:5]]
                        },
                        output_filename=f"report_{job_id}.pdf"
                    )
                    report_paths['pdf'] = f"/api/download/{job_id}/pdf"
                except Exception as e:
                    logger.error(f"PDF generation failed: {str(e)}")
            
            if report_type in ['pptx', 'both']:
                try:
                    slides = [
                        {
                            "title": "Executive Summary",
                            "content": narrative.get("executive_summary", "Report generated successfully.")
                        },
                        {
                            "title": "Key Findings",
                            "content": narrative.get("key_findings", [])
                        },
                        {
                            "title": "Data Statistics",
                            "content": [
                                f"Total Records: {summary['total_rows']}",
                                f"Total Columns: {summary['total_columns']}",
                                f"Columns: {', '.join(summary['columns'][:5])}"
                            ]
                        },
                        {
                            "title": "Recommendations",
                            "content": narrative.get("recommendations", [])
                        }
                    ]
                    
                    if chart_paths:
                        slides[1]["image"] = chart_paths[0]
                    
                    pptx_path = report_gen.generate_powerpoint_report(
                        title="Automated Insight Engine",
                        subtitle="Data Analysis Report",
                        slides_content=slides,
                        output_filename=f"report_{job_id}.pptx"
                    )
                    report_paths['pptx'] = f"/api/download/{job_id}/pptx"
                except Exception as e:
                    logger.error(f"PPTX generation failed: {str(e)}")
            
            app.processing_jobs[job_id] = {
                "status": "completed",
                "file": filename,
                "timestamp": datetime.now().isoformat(),
                "pdf_path": f"report_{job_id}.pdf" if 'pdf' in report_paths else None,
                "pptx_path": f"report_{job_id}.pptx" if 'pptx' in report_paths else None
            }
            
            logger.info(f"Job {job_id} completed successfully")
            
            return jsonify({
                "status": "success",
                "job_id": job_id,
                "reports": report_paths,
                "summary": {
                    "total_rows": summary['total_rows'],
                    "total_columns": summary['total_columns'],
                    "key_findings": len(narrative.get("key_findings", []))
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/download/<job_id>/<format>', methods=['GET'])
    def download_report(job_id, format):
        """Download generated report."""
        try:
            if job_id not in app.processing_jobs:
                return jsonify({"error": "Job not found"}), 404
            
            job = app.processing_jobs[job_id]
            
            output_folder = os.path.abspath(app.config['OUTPUT_FOLDER'])
            
            if format == 'pdf' and job.get('pdf_path'):
                filename = job['pdf_path']
            elif format == 'pptx' and job.get('pptx_path'):
                filename = job['pptx_path']
            else:
                return jsonify({"error": f"Format {format} not available"}), 404
            
            filepath = os.path.join(output_folder, filename)
            filepath = os.path.abspath(filepath)
            
            if not filepath.startswith(output_folder):
                logger.error(f"Security violation: Attempted access outside output folder: {filepath}")
                return jsonify({"error": "Invalid file path"}), 403
            
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return jsonify({"error": f"File not found: {filename}"}), 404
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=os.path.basename(filepath)
            )
            
        except Exception as e:
            logger.error(f"Error downloading report: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    @app.errorhandler(413)
    def too_large(e):
        """Handle file too large error."""
        return jsonify({"error": "File too large (max 100MB)"}), 413

    @app.errorhandler(500)
    def server_error(e):
        """Handle server error."""
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
