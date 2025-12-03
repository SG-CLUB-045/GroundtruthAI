"""
LLM Integration Module
Generates natural language insights using Google Gemini API
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Generates natural language insights from data analysis using Google Gemini.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize InsightGenerator.
        
        Args:
            api_key: Google Gemini API key (uses GEMINI_API_KEY env var if not provided)
            model: Model to use. Default: gemini-2.5-flash
            
        Raises:
            ValueError: If Gemini API key is not provided or client cannot be initialized
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = None
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Please set GEMINI_API_KEY environment variable. "
                "Detailed reports can only be generated through Gemini AI."
            )
        
        try:
            # Try legacy API format first (more stable and widely supported)
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(model)
                self.genai_module = genai
                self.use_new_api = False
                logger.info(f"Initialized Google Gemini client (legacy API) with model: {model}")
            except ImportError:
                # If legacy API not available, try new API format
                try:
                    from google import genai
                    if self.api_key:
                        os.environ['GEMINI_API_KEY'] = self.api_key
                    self.client = genai.Client()
                    self.genai_module = genai
                    self.use_new_api = True
                    logger.info(f"Initialized Google Gemini client (new API) with model: {model}")
                except ImportError:
                    raise ImportError(
                        "Google Generative AI package not installed. "
                        "Please run: pip install google-generativeai"
                    )
            except Exception as legacy_error:
                error_msg = str(legacy_error)
                # If legacy API fails with model error, try new API format
                if "not found" in error_msg.lower() or "404" in error_msg or "is not supported" in error_msg.lower():
                    logger.warning(f"Legacy API model '{model}' not found, trying new API format...")
                    try:
                        from google import genai
                        if self.api_key:
                            os.environ['GEMINI_API_KEY'] = self.api_key
                        self.client = genai.Client()
                        self.genai_module = genai
                        self.use_new_api = True
                        logger.info(f"Initialized Google Gemini client (new API) with model: {model}")
                    except Exception as new_api_error:
                        raise ValueError(
                            f"Model '{model}' is not available. "
                            f"Please use 'gemini-2.5-flash' as the model name. "
                            f"Legacy API error: {error_msg}, New API error: {str(new_api_error)}"
                        )
                else:
                    raise ValueError(
                        f"Error initializing Gemini client: {error_msg}. "
                        "Please verify your GEMINI_API_KEY is correct."
                    )
        except ImportError:
            raise ImportError(
                "Google Generative AI package not installed. "
                "Please run: pip install google-generativeai"
            )
        except ValueError:
            # Re-raise ValueError as-is (already formatted)
            raise
        except Exception as e:
            raise ValueError(
                f"Error initializing Gemini client: {str(e)}. "
                "Please verify your GEMINI_API_KEY is correct."
            )
    
    def is_available(self) -> bool:
        """
        Check if Gemini client is available and ready.
        
        Returns:
            True if Gemini is available, False otherwise
        """
        return self.client is not None

    def generate_executive_summary(
        self,
        metrics: Dict[str, Any],
        context: Optional[str] = None,
        max_length: int = 500
    ) -> str:
        """
        Generate executive summary from metrics using Gemini AI.
        
        Args:
            metrics: Dictionary of calculated metrics
            context: Additional context about the data
            max_length: Maximum length of summary
            
        Returns:
            Executive summary text generated by Gemini
            
        Raises:
            ValueError: If Gemini client is not available
        """
        if not self.client:
            raise ValueError(
                "Gemini API is required to generate executive summary. "
                "Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            prompt = self._build_executive_summary_prompt(metrics, context, max_length)
            
            # Use new API format if available
            if hasattr(self, 'use_new_api') and self.use_new_api:
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt
                    )
                    summary = response.text.strip()
                except Exception as new_api_error:
                    error_msg = str(new_api_error)
                    # If model not found, try alternative models
                    if "404" in error_msg or "not found" in error_msg.lower() or "not supported" in error_msg.lower():
                        logger.warning(f"Model {self.model} not found, trying gemini-2.5-flash...")
                        # Try gemini-2.5-flash as fallback
                        alternative_models = ["gemini-2.5-flash"]
                        summary = None
                        for alt_model in alternative_models:
                            try:
                                logger.info(f"Trying model: {alt_model}")
                                response = self.client.models.generate_content(
                                    model=alt_model,
                                    contents=prompt
                                )
                                summary = response.text.strip()
                                self.model = alt_model  # Update model for future calls
                                logger.info(f"Successfully used model: {alt_model}")
                                break
                            except Exception:
                                continue
                        
                        if summary is None:
                            raise ValueError(
                                f"None of the models worked. Original error: {error_msg}. "
                                "Please check your API key and try updating: pip install --upgrade google-generativeai"
                            )
                    else:
                        raise
            else:
                # Legacy API format
                response = self.client.generate_content(prompt)
                summary = response.text.strip()
            
            logger.info("Generated executive summary using Gemini")
            return summary[:max_length * 2]  # Approximate character limit
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            raise ValueError(
                f"Failed to generate executive summary using Gemini: {str(e)}. "
                "Please verify your API key and try again. You may need to update: pip install --upgrade google-generativeai"
            )

    def generate_key_findings(
        self,
        metrics: Dict[str, Any],
        num_findings: int = 5
    ) -> List[str]:
        """
        Generate key findings from metrics using Gemini AI.
        
        Args:
            metrics: Dictionary of calculated metrics
            num_findings: Number of findings to generate
            
        Returns:
            List of key findings generated by Gemini
            
        Raises:
            ValueError: If Gemini client is not available
        """
        if not self.client:
            raise ValueError(
                "Gemini API is required to generate key findings. "
                "Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            prompt = self._build_findings_prompt(metrics, num_findings)
            
            # Use new API format if available
            if hasattr(self, 'use_new_api') and self.use_new_api:
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt
                    )
                except Exception as e:
                    if "404" in str(e) or "not found" in str(e).lower():
                        # Try alternative models
                        for alt_model in ["gemini-2.5-flash"]:
                            try:
                                response = self.client.models.generate_content(
                                    model=alt_model,
                                    contents=prompt
                                )
                                self.model = alt_model
                                break
                            except Exception:
                                continue
                    else:
                        raise
            else:
                # Legacy API format
                response = self.client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse findings from response
            findings = []
            for line in response_text.split("\n"):
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("•") or 
                           line.startswith("*") or line[0].isdigit()):
                    # Remove bullet points and numbering
                    finding = line.lstrip("-•*0123456789. ").strip()
                    if finding:
                        findings.append(finding)
            
            if not findings:
                # If no bullet points found, split by sentences
                findings = [s.strip() for s in response_text.split(".") if s.strip()][:num_findings]
            
            logger.info(f"Generated {len(findings)} key findings using Gemini")
            return findings[:num_findings] if findings else [response_text[:200]]
            
        except Exception as e:
            logger.error(f"Error generating findings: {str(e)}")
            raise ValueError(
                f"Failed to generate key findings using Gemini: {str(e)}. "
                "Please verify your API key and try again."
            )

    def generate_recommendations(
        self,
        metrics: Dict[str, Any],
        context: Optional[str] = None,
        num_recommendations: int = 5
    ) -> List[str]:
        """
        Generate actionable recommendations from metrics using Gemini AI.
        
        Args:
            metrics: Dictionary of calculated metrics
            context: Additional business context
            num_recommendations: Number of recommendations
            
        Returns:
            List of recommendations generated by Gemini
            
        Raises:
            ValueError: If Gemini client is not available
        """
        if not self.client:
            raise ValueError(
                "Gemini API is required to generate recommendations. "
                "Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            prompt = self._build_recommendations_prompt(metrics, context, num_recommendations)
            
            # Use new API format if available
            if hasattr(self, 'use_new_api') and self.use_new_api:
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt
                    )
                except Exception as e:
                    if "404" in str(e) or "not found" in str(e).lower():
                        # Try alternative models
                        for alt_model in ["gemini-2.5-flash"]:
                            try:
                                response = self.client.models.generate_content(
                                    model=alt_model,
                                    contents=prompt
                                )
                                self.model = alt_model
                                break
                            except Exception:
                                continue
                    else:
                        raise
            else:
                # Legacy API format
                response = self.client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse recommendations from response
            recommendations = []
            for line in response_text.split("\n"):
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("•") or 
                           line.startswith("*") or line[0].isdigit()):
                    # Remove bullet points and numbering
                    rec = line.lstrip("-•*0123456789. ").strip()
                    if rec:
                        recommendations.append(rec)
            
            if not recommendations:
                # If no bullet points found, split by sentences
                recommendations = [s.strip() for s in response_text.split(".") if s.strip()][:num_recommendations]
            
            logger.info(f"Generated {len(recommendations)} recommendations using Gemini")
            return recommendations[:num_recommendations] if recommendations else [response_text[:200]]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise ValueError(
                f"Failed to generate recommendations using Gemini: {str(e)}. "
                "Please verify your API key and try again."
            )

    def generate_insight_narrative(
        self,
        metrics: Dict[str, Any],
        title: str = "Data Analysis Report",
        detailed: bool = False
    ) -> Dict[str, str]:
        """
        Generate comprehensive insight narrative.
        
        Args:
            metrics: Dictionary of calculated metrics
            title: Report title
            detailed: Whether to generate detailed narrative
            
        Returns:
            Dictionary with different narrative sections
        """
        try:
            narrative = {
                "title": title,
                "generated_at": datetime.now().isoformat(),
                "executive_summary": self.generate_executive_summary(metrics),
                "key_findings": self.generate_key_findings(metrics),
                "recommendations": self.generate_recommendations(metrics)
            }
            
            if detailed:
                narrative["detailed_analysis"] = self.generate_detailed_analysis(metrics)
            
            logger.info("Generated comprehensive insight narrative")
            return narrative
            
        except Exception as e:
            logger.error(f"Error generating narrative: {str(e)}")
            return {
                "title": title,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    def generate_detailed_analysis(
        self,
        metrics: Dict[str, Any]
    ) -> str:
        """
        Generate detailed strategic business analysis using Gemini AI.
        
        Args:
            metrics: Dictionary of calculated metrics
            
        Returns:
            Detailed analysis text generated by Gemini
            
        Raises:
            ValueError: If Gemini client is not available
        """
        if not self.client:
            raise ValueError(
                "Gemini API is required to generate detailed analysis. "
                "Please set GEMINI_API_KEY environment variable."
            )
        
        try:
            prompt = f"""You are a senior business strategist. Provide a comprehensive strategic analysis of the following business metrics:

{json.dumps(metrics, indent=2, default=str)}

Your analysis should include:

1. **Strategic Performance Assessment**
   - Overall business health and competitive position
   - Key performance drivers and constraints
   - Market positioning insights

2. **Revenue & Profitability Analysis**
   - Revenue growth patterns and opportunities
   - Profit margin optimization potential
   - Cost structure efficiency

3. **Growth Opportunities**
   - High-impact growth levers
   - Market expansion possibilities
   - Product/service optimization areas

4. **Risk & Threat Analysis**
   - Critical vulnerabilities
   - Competitive threats
   - Market risks

5. **Strategic Recommendations**
   - Priority actions for competitive advantage
   - Resource allocation strategies
   - Long-term strategic positioning

Write in a professional, strategic tone suitable for executive leadership. Focus on insights that create competitive advantage and drive sustainable business growth."""
            
            # Use new API format if available
            if hasattr(self, 'use_new_api') and self.use_new_api:
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt
                    )
                except Exception as e:
                    if "404" in str(e) or "not found" in str(e).lower():
                        # Try alternative models
                        for alt_model in ["gemini-2.5-flash"]:
                            try:
                                response = self.client.models.generate_content(
                                    model=alt_model,
                                    contents=prompt
                                )
                                self.model = alt_model
                                break
                            except Exception:
                                continue
                    else:
                        raise
            else:
                # Legacy API format
                response = self.client.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating detailed analysis: {str(e)}")
            raise ValueError(
                f"Failed to generate detailed analysis using Gemini: {str(e)}. "
                "Please verify your API key and try again."
            )

    def _build_executive_summary_prompt(
        self,
        metrics: Dict[str, Any],
        context: Optional[str],
        max_length: int
    ) -> str:
        """Build prompt for executive summary."""
        prompt = f"""You are a senior business strategist and C-level advisor. Based on the following comprehensive business metrics, generate a strategic executive summary (max {max_length} words) that:

1. Highlights critical business performance indicators
2. Identifies strategic opportunities and threats
3. Provides actionable insights for leadership decision-making
4. Focuses on revenue growth, profitability, and competitive positioning

Business Metrics:
{json.dumps(metrics, indent=2, default=str)}"""
        
        if context:
            prompt += f"\n\nBusiness Context: {context}"
        
        prompt += "\n\nWrite in a professional, strategic tone suitable for board-level presentation. Focus on what matters most for business growth and competitive advantage."
        return prompt

    def _build_findings_prompt(
        self,
        metrics: Dict[str, Any],
        num_findings: int
    ) -> str:
        """Build prompt for key findings."""
        return f"""You are a business intelligence analyst. From the following comprehensive metrics, extract exactly {num_findings} strategic business findings that:

1. Reveal hidden patterns and opportunities
2. Identify competitive advantages or disadvantages
3. Highlight revenue drivers and growth levers
4. Uncover operational inefficiencies or optimization opportunities
5. Provide insights not obvious from surface-level analysis

Business Metrics:
{json.dumps(metrics, indent=2, default=str)}

Format each finding as a separate bullet point starting with "-" or "•". Each finding should be:
- Specific and data-driven with numbers
- Strategic and actionable
- Focused on business impact (revenue, profit, growth, efficiency)
- Unique insights that competitors might miss"""

    def _build_recommendations_prompt(
        self,
        metrics: Dict[str, Any],
        context: Optional[str],
        num_recommendations: int
    ) -> str:
        """Build prompt for recommendations."""
        prompt = f"""You are a strategic business consultant. Based on these comprehensive business metrics, provide exactly {num_recommendations} strategic, high-impact recommendations that:

1. Drive measurable revenue growth or cost optimization
2. Improve competitive positioning and market share
3. Optimize resource allocation and ROI
4. Address critical business risks and opportunities
5. Include specific, actionable steps with expected outcomes

Business Metrics:
{json.dumps(metrics, indent=2, default=str)}"""
        
        if context:
            prompt += f"\n\nBusiness Context: {context}"
        
        prompt += "\n\nFormat each recommendation as a separate bullet point starting with \"-\" or \"•\". Each recommendation should include:\n- Clear action statement\n- Expected business impact (revenue, profit, efficiency)\n- Priority level (High/Medium/Low)\n- Implementation complexity\n\nFocus on recommendations that create competitive advantage and drive sustainable growth."
        return prompt

