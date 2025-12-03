"""
Report Generation Module
Creates PDF and PowerPoint reports with charts, tables, and insights
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.dml.color import RGBColor
except ImportError:
    pass

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    # Use HexColor for RGB colors
    def ReportLabRGB(r, g, b):
        return HexColor(f"#{r:02x}{g:02x}{b:02x}")
    REPORTLAB_AVAILABLE = True
except ImportError:
    # Fallback if reportlab not available
    ReportLabRGB = None
    REPORTLAB_AVAILABLE = False

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates PDF and PowerPoint reports with data visualizations and insights.
    """

    def __init__(self, output_dir: str = "./output"):
        """
        Initialize ReportGenerator.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.charts: List[str] = []

    def create_chart(
        self,
        data: Dict[str, Any],
        chart_type: str = "bar",
        title: str = "Chart",
        xlabel: str = "",
        ylabel: str = "",
        figsize: Tuple[int, int] = (10, 6)
    ) -> str:
        """
        Create a chart and save it as an image.
        
        Args:
            data: Dictionary with chart data
            chart_type: Type of chart ('bar', 'line', 'pie', 'scatter')
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size (width, height)
            
        Returns:
            Path to saved chart image
        """
        try:
            fig, ax = plt.subplots(figsize=figsize)
            fig.patch.set_facecolor('white')
            
            if chart_type == "bar":
                x_data = list(data.keys())[:20]  # Limit to 20 items
                y_data = list(data.values())[:20]
                ax.bar(x_data, y_data, color='#2E86AB', alpha=0.8)
                ax.set_xticks(range(len(x_data)))
                ax.set_xticklabels(x_data, rotation=45, ha='right')
            
            elif chart_type == "line":
                x_data = list(data.keys())
                y_data = list(data.values())
                ax.plot(range(len(x_data)), y_data, marker='o', color='#2E86AB', linewidth=2)
                ax.set_xticks(range(len(x_data)))
                ax.set_xticklabels(x_data, rotation=45, ha='right')
            
            elif chart_type == "pie":
                labels = list(data.keys())[:10]
                sizes = list(data.values())[:10]
                colors_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E',
                                 '#BC4749', '#2C7873', '#4C9A9B', '#8B0000', '#FF6B6B']
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors_palette, startangle=90)
            
            elif chart_type == "scatter":
                x_data = list(range(len(data)))
                y_data = list(data.values())
                ax.scatter(x_data, y_data, s=100, alpha=0.6, color='#2E86AB')
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            if xlabel:
                ax.set_xlabel(xlabel, fontsize=11)
            if ylabel:
                ax.set_ylabel(ylabel, fontsize=11)
            
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save chart
            chart_path = self.output_dir / f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            plt.savefig(str(chart_path), dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.charts.append(str(chart_path))
            logger.info(f"Created {chart_type} chart: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return ""

    def create_table_image(
        self,
        data: Dict[str, List[Any]],
        title: str = "Data Table",
        rows_limit: int = 10
    ) -> str:
        """
        Create a table as an image.
        
        Args:
            data: Dictionary with column names as keys and lists as values
            title: Table title
            rows_limit: Maximum rows to display
            
        Returns:
            Path to saved table image
        """
        try:
            # Create DataFrame from data
            df = pd.DataFrame(data)
            df = df.head(rows_limit)
            
            fig, ax = plt.subplots(figsize=(12, max(4, len(df) * 0.3)))
            ax.axis('tight')
            ax.axis('off')
            
            # Create table
            table = ax.table(
                cellText=df.values,
                colLabels=df.columns,
                cellLoc='center',
                loc='center',
                colWidths=[1 / len(df.columns) for _ in df.columns]
            )
            
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            
            # Style header
            for i in range(len(df.columns)):
                table[(0, i)].set_facecolor('#2E86AB')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Alternate row colors
            for i in range(1, len(df) + 1):
                for j in range(len(df.columns)):
                    if i % 2 == 0:
                        table[(i, j)].set_facecolor('#F0F0F0')
                    else:
                        table[(i, j)].set_facecolor('#FFFFFF')
            
            plt.title(title, fontsize=12, fontweight='bold', pad=20)
            plt.tight_layout()
            
            table_path = self.output_dir / f"table_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            plt.savefig(str(table_path), dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Created table image: {table_path}")
            return str(table_path)
            
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            return ""

    def generate_pdf_report(
        self,
        title: str,
        subtitle: str,
        sections: Dict[str, str],
        tables: Optional[List[Dict[str, Any]]] = None,
        charts: Optional[List[str]] = None,
        insights: Optional[Dict[str, Any]] = None,
        output_filename: str = "report.pdf"
    ) -> str:
        """
        Generate a comprehensive PDF business report.
        
        Args:
            title: Report title
            subtitle: Report subtitle
            sections: Dictionary of section_name: section_content
            tables: List of table data dictionaries
            charts: List of chart image paths
            insights: Dictionary of insights
            output_filename: Output PDF filename
            
        Returns:
            Path to generated PDF
        """
        try:
            if not REPORTLAB_AVAILABLE or ReportLabRGB is None:
                raise ImportError("ReportLab not properly imported")
            
            output_path = self.output_dir / output_filename
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Enhanced custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=ReportLabRGB(46, 134, 171),
                spaceAfter=12,
                alignment=1,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontSize=16,
                textColor=ReportLabRGB(100, 100, 100),
                spaceAfter=20,
                alignment=1,
                fontName='Helvetica'
            )
            
            heading2_style = ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=ReportLabRGB(46, 134, 171),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            heading3_style = ParagraphStyle(
                'CustomHeading3',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=ReportLabRGB(70, 70, 70),
                spaceAfter=8,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                textColor=ReportLabRGB(50, 50, 50),
                spaceAfter=6,
                leading=14,
                fontName='Helvetica'
            )
            
            # Cover Page
            story.append(Spacer(1, 1.5*inch))
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(subtitle, subtitle_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Add metadata
            metadata = f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}"
            story.append(Paragraph(metadata, normal_style))
            story.append(PageBreak())
            
            # Table of Contents placeholder
            story.append(Paragraph("Table of Contents", heading2_style))
            toc_items = list(sections.keys())
            if insights:
                toc_items.extend(["Key Insights", "Key Findings", "Recommendations"])
            if tables:
                toc_items.append("Data Tables")
            if charts:
                toc_items.append("Visualizations")
            
            for i, item in enumerate(toc_items[:10], 1):  # Limit to 10 items
                story.append(Paragraph(f"{i}. {item}", normal_style))
            story.append(PageBreak())
            
            # Add sections with enhanced formatting
            for section_name, section_content in sections.items():
                story.append(Paragraph(section_name, heading2_style))
                
                # Format content with line breaks
                content_lines = str(section_content).split('\n')
                for line in content_lines:
                    if line.strip():
                        if line.strip().startswith('•') or line.strip().startswith('-'):
                            story.append(Paragraph(line.strip(), normal_style))
                        else:
                            # Check if it's a bullet point
                            if ':' in line and not line.startswith(' '):
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    story.append(Paragraph(f"<b>{parts[0]}:</b> {parts[1].strip()}", normal_style))
                                else:
                                    story.append(Paragraph(line.strip(), normal_style))
                            else:
                                story.append(Paragraph(line.strip(), normal_style))
                
                story.append(Spacer(1, 0.3*inch))
            
            # Add Strategic Recommendations section first (if available)
            if insights and "Strategic Recommendations" in insights:
                story.append(PageBreak())
                story.append(Paragraph("Prioritized Strategic Recommendations", heading2_style))
                story.append(Spacer(1, 0.2*inch))
                
                strategic_recs = insights["Strategic Recommendations"]
                if isinstance(strategic_recs, list):
                    for rec in strategic_recs[:10]:
                        story.append(Paragraph(rec, normal_style))
                        story.append(Spacer(1, 0.1*inch))
                story.append(Spacer(1, 0.2*inch))
            
            # Add insights section with better formatting
            if insights:
                story.append(PageBreak())
                story.append(Paragraph("Strategic Insights & Analysis", heading2_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Executive Summary if available
                if "Executive Summary" in insights:
                    story.append(Paragraph("Executive Summary", heading3_style))
                    exec_summary = insights["Executive Summary"]
                    if isinstance(exec_summary, str):
                        story.append(Paragraph(exec_summary, normal_style))
                    story.append(Spacer(1, 0.2*inch))
                
                # Key Findings
                if "Key Findings" in insights:
                    story.append(Paragraph("Key Strategic Findings", heading3_style))
                    findings = insights["Key Findings"]
                    if isinstance(findings, list):
                        for finding in findings:
                            story.append(Paragraph(f"• {finding}", normal_style))
                    else:
                        story.append(Paragraph(str(findings), normal_style))
                    story.append(Spacer(1, 0.2*inch))
                
                # Recommendations
                if "Recommendations" in insights:
                    story.append(Paragraph("AI-Generated Strategic Recommendations", heading3_style))
                    recommendations = insights["Recommendations"]
                    if isinstance(recommendations, list):
                        for rec in recommendations:
                            story.append(Paragraph(f"• {rec}", normal_style))
                    else:
                        story.append(Paragraph(str(recommendations), normal_style))
                    story.append(Spacer(1, 0.2*inch))
            
            # Add tables with enhanced styling
            if tables:
                story.append(PageBreak())
                story.append(Paragraph("Data Analysis Tables", heading2_style))
                story.append(Spacer(1, 0.2*inch))
                
                for table_data in tables:
                    story.append(Paragraph(table_data.get('title', 'Data Table'), heading3_style))
                    
                    # Create table
                    table_content = table_data.get('data', [])
                    if table_content and len(table_content) > 0:
                        num_cols = len(table_content[0])
                        col_widths = [6.5*inch / num_cols] * num_cols
                        
                        table_obj = Table(table_content, colWidths=col_widths)
                        table_style = TableStyle([
                            # Header row
                            ('BACKGROUND', (0, 0), (-1, 0), ReportLabRGB(46, 134, 171)),
                            ('TEXTCOLOR', (0, 0), (-1, 0), ReportLabRGB(255, 255, 255)),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 11),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('TOPPADDING', (0, 0), (-1, 0), 12),
                            # Data rows
                            ('BACKGROUND', (0, 1), (-1, -1), ReportLabRGB(255, 255, 255)),
                            ('TEXTCOLOR', (0, 1), (-1, -1), ReportLabRGB(50, 50, 50)),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 10),
                            ('GRID', (0, 0), (-1, -1), 0.5, ReportLabRGB(200, 200, 200)),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [ReportLabRGB(245, 245, 245), ReportLabRGB(255, 255, 255)]),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ])
                        table_obj.setStyle(table_style)
                        story.append(table_obj)
                    story.append(Spacer(1, 0.3*inch))
            
            # Add charts with titles
            if charts:
                story.append(PageBreak())
                story.append(Paragraph("Data Visualizations", heading2_style))
                story.append(Spacer(1, 0.2*inch))
                
                for idx, chart_path in enumerate(charts, 1):
                    if os.path.exists(chart_path):
                        try:
                            # Add chart number
                            story.append(Paragraph(f"Chart {idx}", heading3_style))
                            story.append(Spacer(1, 0.1*inch))
                            
                            # Add chart image
                            story.append(RLImage(chart_path, width=6.5*inch, height=4.5*inch))
                            story.append(Spacer(1, 0.3*inch))
                        except Exception as e:
                            logger.warning(f"Could not add chart {chart_path}: {str(e)}")
            
            # Add footer/appendices
            story.append(PageBreak())
            story.append(Paragraph("Appendix", heading2_style))
            story.append(Paragraph("Report Metadata", heading3_style))
            story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Paragraph(f"Total Sections: {len(sections)}", normal_style))
            story.append(Paragraph(f"Total Charts: {len(charts) if charts else 0}", normal_style))
            story.append(Paragraph(f"Total Tables: {len(tables) if tables else 0}", normal_style))
            
            doc.build(story)
            logger.info(f"Generated comprehensive PDF report: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def generate_powerpoint_report(
        self,
        title: str,
        subtitle: str,
        slides_content: List[Dict[str, Any]],
        output_filename: str = "report.pptx"
    ) -> str:
        """
        Generate a PowerPoint report.
        
        Args:
            title: Presentation title
            subtitle: Presentation subtitle
            slides_content: List of slide dictionaries with content
            output_filename: Output PPTX filename
            
        Returns:
            Path to generated PPTX
        """
        try:
            prs = Presentation()
            prs.slide_width = Inches(10)
            prs.slide_height = Inches(7.5)
            
            # Define color scheme
            DARK_BLUE = RGBColor(46, 134, 171)
            LIGHT_GRAY = RGBColor(240, 240, 240)
            WHITE = RGBColor(255, 255, 255)
            DARK_TEXT = RGBColor(50, 50, 50)
            
            # Slide 1: Title Slide
            title_slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(title_slide_layout)
            
            # Add background color
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = DARK_BLUE
            
            # Add title
            left = Inches(0.5)
            top = Inches(2.5)
            width = Inches(9)
            height = Inches(1.5)
            
            title_box = slide.shapes.add_textbox(left, top, width, height)
            title_frame = title_box.text_frame
            title_frame.text = title
            title_frame.paragraphs[0].font.size = Pt(54)
            title_frame.paragraphs[0].font.bold = True
            title_frame.paragraphs[0].font.color.rgb = WHITE
            title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            
            # Add subtitle
            subtitle_box = slide.shapes.add_textbox(left, Inches(4.2), width, Inches(1))
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = subtitle
            subtitle_frame.paragraphs[0].font.size = Pt(28)
            subtitle_frame.paragraphs[0].font.color.rgb = RGBColor(200, 200, 200)
            subtitle_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            
            # Add date
            date_box = slide.shapes.add_textbox(left, Inches(6.5), width, Inches(0.5))
            date_frame = date_box.text_frame
            date_frame.text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
            date_frame.paragraphs[0].font.size = Pt(14)
            date_frame.paragraphs[0].font.color.rgb = RGBColor(150, 150, 150)
            date_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            
            # Add content slides
            for slide_data in slides_content:
                self._add_content_slide(prs, slide_data, DARK_BLUE, LIGHT_GRAY, DARK_TEXT)
            
            output_path = self.output_dir / output_filename
            prs.save(str(output_path))
            logger.info(f"Generated PowerPoint report: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating PowerPoint: {str(e)}")
            raise

    def _add_content_slide(
        self,
        prs: Presentation,
        slide_data: Dict[str, Any],
        dark_blue: RGBColor,
        light_gray: RGBColor,
        dark_text: RGBColor
    ) -> None:
        """Add a content slide to presentation."""
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        
        # Add header background
        header_shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(1))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = dark_blue
        header_shape.line.color.rgb = dark_blue
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.7))
        title_frame = title_box.text_frame
        title_frame.text = slide_data.get('title', 'Slide')
        title_frame.paragraphs[0].font.size = Pt(40)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        
        # Add content
        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(9), Inches(5.7))
        text_frame = content_box.text_frame
        text_frame.word_wrap = True
        
        content = slide_data.get('content', '')
        if isinstance(content, list):
            for idx, item in enumerate(content):
                if idx > 0:
                    text_frame.add_paragraph()
                p = text_frame.paragraphs[idx]
                p.text = f"• {item}" if idx > 0 else item
                p.font.size = Pt(18)
                p.font.color.rgb = dark_text
                p.level = 0
        else:
            text_frame.text = str(content)
            text_frame.paragraphs[0].font.size = Pt(18)
            text_frame.paragraphs[0].font.color.rgb = dark_text
        
        # Add image if provided
        if 'image' in slide_data and os.path.exists(slide_data['image']):
            try:
                slide.shapes.add_picture(
                    slide_data['image'],
                    Inches(0.5),
                    Inches(1.3),
                    width=Inches(9),
                    height=Inches(5.7)
                )
            except Exception as e:
                logger.warning(f"Could not add image: {str(e)}")

    def cleanup_temp_files(self) -> None:
        """Clean up temporary chart files."""
        try:
            for chart_path in self.charts:
                if os.path.exists(chart_path):
                    os.remove(chart_path)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
