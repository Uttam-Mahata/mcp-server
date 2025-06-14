import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone, timedelta
import google.genai as genai
from google.genai import types
import asyncio
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger(__name__)

class AnalysisType(str, Enum):
    """Types of code analysis"""
    COMPREHENSIVE = "comprehensive"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"

class ReviewLevel(str, Enum):
    """Code review thoroughness levels"""
    QUICK = "quick"
    STANDARD = "standard"
    THOROUGH = "thorough"
    EXHAUSTIVE = "exhaustive"

class DocumentationType(str, Enum):
    """Documentation generation types"""
    API = "api"
    USER_GUIDE = "user_guide"
    DEVELOPER_GUIDE = "developer_guide"
    COMPREHENSIVE = "comprehensive"

class CodeAnalysisResult(BaseModel):
    """Structured code analysis result"""
    summary: str = Field(description="Brief summary of the analysis")
    quality_score: int = Field(ge=0, le=100, description="Overall quality score (0-100)")
    issues: List[Dict[str, Any]] = Field(description="List of identified issues")
    suggestions: List[str] = Field(description="Improvement suggestions")
    complexity_metrics: Dict[str, Any] = Field(description="Code complexity metrics")
    security_findings: List[Dict[str, Any]] = Field(description="Security-related findings")

class GeminiClient:
    """
    Advanced Google Gemini client with agentic capabilities
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-thinking-exp", enable_thinking: bool = True):
        self.api_key = api_key
        self.model = model
        self.enable_thinking = enable_thinking
        self.client = genai.Client(api_key=api_key)
        self._cache_store = {}
        
    async def _create_cached_content(self, content: str, ttl_hours: int = 1) -> Optional[str]:
        """Create cached content for large context"""
        try:
            if len(content) < 1024:  # Only cache larger content
                return None
                
            expire_time = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
            
            cache = await self.client.caches.create(
                config=types.CreateCachedContentConfig(
                    model=self.model,
                    contents=[content],
                    ttl=f"{ttl_hours * 3600}s"
                )
            )
            return cache.name
        except Exception as e:
            logger.warning(f"Failed to create cache: {e}")
            return None
    
    async def _generate_with_thinking(
        self, 
        prompt: str, 
        response_schema: Optional[Any] = None,
        thinking_budget: Optional[int] = None,
        cached_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response with thinking capabilities"""
        
        # Create the generation config
        config_params = {
            "temperature": 0.1,
            "top_k": 20,
            "top_p": 0.8
        }
        
        # Add response schema for structured output
        if response_schema:
            config_params["response_schema"] = response_schema
            config_params["response_mime_type"] = "application/json"
        
        config = types.GenerateContentConfig(**config_params)
        
        # Prepare contents
        contents = [prompt]
        if cached_content:
            contents = [types.Part(cached_content=cached_content), prompt]
        
        try:
            # Note: generate_content is NOT async in the current SDK
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            
            result = {
                "content": response.text,
                "usage": {
                    "input_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "output_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                }
            }
            
            # Add thinking information if available
            if hasattr(response.usage_metadata, 'thoughts_token_count'):
                result["usage"]["thinking_tokens"] = response.usage_metadata.thoughts_token_count
            
            return result
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    async def analyze_code(
        self, 
        code: str, 
        language: str = "auto", 
        analysis_type: str = "comprehensive",
        context: str = ""
    ) -> Dict[str, Any]:
        """Analyze code with Gemini's advanced reasoning"""
        
        prompt = f"""
Analyze the following {language} code with a focus on {analysis_type} analysis.

Context: {context}

Code:
```{language}
{code}
```

Provide a comprehensive analysis including:
1. Code quality assessment
2. Security vulnerabilities
3. Performance considerations
4. Maintainability factors
5. Best practice adherence
6. Specific improvement suggestions

Be thorough and provide actionable insights.

Please format your response as JSON with the following structure:
{{
  "summary": "Brief summary of the analysis",
  "quality_score": 85,
  "issues": [
    {{"type": "performance", "description": "Issue description", "severity": "medium"}}
  ],
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "complexity_metrics": {{"cyclomatic_complexity": 5}},
  "security_findings": [
    {{"type": "vulnerability", "description": "Security issue description"}}
  ]
}}
"""
        
        # Create cache for large code
        cached_content = await self._create_cached_content(code) if len(code) > 2000 else None
        
        return await self._generate_with_thinking(
            prompt=prompt,
            cached_content=cached_content
        )
    
    async def suggest_improvements(
        self, 
        code: str, 
        language: str = "auto",
        focus_areas: List[str] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """Generate specific improvement suggestions"""
        
        focus_str = ", ".join(focus_areas) if focus_areas else "general improvements"
        
        prompt = f"""
Review this {language} code and suggest specific improvements focusing on: {focus_str}

Context: {context}

Code:
```{language}
{code}
```

For each suggestion, provide:
1. The specific issue or opportunity
2. The improved code snippet
3. Explanation of why this is better
4. Impact assessment (performance, readability, maintainability)

Prioritize suggestions by impact and feasibility.
"""
        
        return await self._generate_with_thinking(
            prompt=prompt
        )
    
    async def generate_documentation(
        self, 
        code: str, 
        doc_type: str = "comprehensive",
        format: str = "markdown",
        context: str = ""
    ) -> Dict[str, Any]:
        """Generate intelligent documentation"""
        
        prompt = f"""
Generate {doc_type} documentation for the following code in {format} format.

Context: {context}

Code:
```
{code}
```

Include:
- Clear function/class descriptions
- Parameter explanations with types
- Return value descriptions
- Usage examples
- Error handling notes
- Dependencies and requirements
- Performance considerations if relevant

Make the documentation clear, comprehensive, and developer-friendly.
"""
        
        return await self._generate_with_thinking(
            prompt=prompt
        )
    
    async def explain_code(
        self, 
        code: str, 
        level: str = "intermediate",
        focus: str = "functionality",
        context: str = ""
    ) -> Dict[str, Any]:
        """Explain code functionality at different levels"""
        
        prompt = f"""
Explain this code at a {level} level, focusing on {focus}.

Context: {context}

Code:
```
{code}
```

Provide:
1. High-level overview of what the code does
2. Step-by-step breakdown of the logic
3. Key concepts and patterns used
4. Input/output flow
5. Important implementation details
6. Potential edge cases or considerations

Tailor the explanation to a {level} audience.
"""
        
        return await self._generate_with_thinking(
            prompt=prompt
        )
    
    async def review_pull_request(
        self, 
        diff: str, 
        context: str = "",
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive pull request review"""
        
        focus_str = ", ".join(focus_areas) if focus_areas else "all aspects"
        
        prompt = f"""
Review this pull request diff focusing on: {focus_str}

Context: {context}

Diff:
```diff
{diff}
```

Provide a comprehensive review including:
1. Overall assessment and summary
2. Code quality evaluation
3. Security considerations
4. Performance implications
5. Testing recommendations
6. Documentation needs
7. Specific line-by-line feedback for critical issues
8. Approval recommendation (approve/request changes/needs work)

Be constructive and specific in your feedback.
"""
        
        return await self._generate_with_thinking(
            prompt=prompt
        )
    
    async def generate_tests(
        self, 
        code: str, 
        test_framework: str = "auto",
        coverage_level: str = "comprehensive",
        context: str = ""
    ) -> Dict[str, Any]:
        """Generate intelligent test cases"""
        
        prompt = f"""
Generate {coverage_level} test cases for the following code using {test_framework} framework.

Context: {context}

Code:
```
{code}
```

Generate tests that cover:
1. Happy path scenarios
2. Edge cases and boundary conditions
3. Error handling and exceptions
4. Input validation
5. Integration scenarios if applicable
6. Performance tests if relevant

Provide:
- Complete test code
- Test descriptions and rationale
- Setup and teardown requirements
- Mock/stub suggestions
- Coverage analysis
"""
        
        return await self._generate_with_thinking(
            prompt=prompt
        )
    
    async def analyze_repository_structure(
        self, 
        repo_data: Dict[str, Any],
        focus_areas: List[str] = None,
        depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Analyze entire repository structure and architecture"""
        
        focus_str = ", ".join(focus_areas) if focus_areas else "overall architecture"
        
        prompt = f"""
Analyze this repository structure and provide {depth} insights focusing on: {focus_str}

Repository Data:
{json.dumps(repo_data, indent=2)}

Provide analysis on:
1. Project architecture and organization
2. Code structure and patterns
3. Dependencies and technology stack
4. Development workflow and practices
5. Documentation quality
6. Testing strategy
7. Security posture
8. Performance considerations
9. Scalability factors
10. Improvement recommendations

Give specific, actionable recommendations for each area.
"""
        
        # Cache large repository data
        cached_content = await self._create_cached_content(json.dumps(repo_data))
        
        return await self._generate_with_thinking(
            prompt=prompt,
            cached_content=cached_content
        )
    
    async def triage_issues(
        self, 
        issues: List[Dict[str, Any]],
        criteria: str = "default"
    ) -> Dict[str, Any]:
        """Intelligent issue triage and prioritization"""
        
        prompt = f"""
Analyze and triage these GitHub issues using {criteria} criteria.

Issues:
{json.dumps(issues, indent=2)}

For each issue, provide:
1. Priority level (Critical/High/Medium/Low)
2. Estimated effort (Small/Medium/Large/Extra Large)
3. Category classification
4. Dependencies and blockers
5. Recommended assignee type (senior/junior/specialist)
6. Timeline suggestion

Also provide:
- Overall prioritization recommendations
- Resource allocation suggestions
- Sprint planning insights
- Risk assessment
"""
        
        return await self._generate_with_thinking(
            prompt=prompt,
            thinking_budget=2000
        )
    
    async def comprehensive_code_review(
        self, 
        pr_data: Dict[str, Any],
        review_level: str = "thorough"
    ) -> Dict[str, Any]:
        """Comprehensive code review with full context"""
        
        prompt = f"""
Perform a {review_level} code review of this pull request.

PR Data:
{json.dumps(pr_data, indent=2)}

Provide a comprehensive review covering:

1. SUMMARY
   - Overall assessment
   - Key changes overview
   - Impact analysis

2. CODE QUALITY
   - Architecture and design
   - Code organization
   - Best practices adherence
   - Maintainability

3. SECURITY
   - Vulnerability assessment
   - Security best practices
   - Data handling review

4. PERFORMANCE
   - Performance implications
   - Optimization opportunities
   - Resource usage

5. TESTING
   - Test coverage analysis
   - Testing strategy review
   - Missing test scenarios

6. DOCUMENTATION
   - Code documentation
   - API documentation
   - User-facing documentation

7. SPECIFIC FEEDBACK
   - Line-by-line critical issues
   - Specific improvement suggestions
   - Alternative approaches

8. RECOMMENDATIONS
   - Approval status
   - Required changes
   - Next steps

Be thorough, constructive, and provide actionable feedback.
"""
        
        # Cache large PR data
        cached_content = await self._create_cached_content(json.dumps(pr_data))
        
        return await self._generate_with_thinking(
            prompt=prompt,
            thinking_budget=3500,
            cached_content=cached_content
        )
    
    async def generate_repository_summary(self, repo_data: Dict[str, Any]) -> str:
        """Generate intelligent repository summary"""
        
        prompt = f"""
Generate a comprehensive summary of this repository.

Repository Data:
{json.dumps(repo_data, indent=2)}

Include:
1. Project overview and purpose
2. Technology stack and architecture
3. Key features and capabilities
4. Development status and activity
5. Code quality assessment
6. Documentation status
7. Community and contribution info
8. Getting started guidance
9. Notable strengths and areas for improvement

Make it informative and accessible to both technical and non-technical audiences.
"""
        
        result = await self._generate_with_thinking(
            prompt=prompt,
            thinking_budget=1500
        )
        
        return result.get("content", "")
    
    async def analyze_repository_metrics(self, metrics: Dict[str, Any]) -> str:
        """Analyze repository metrics and provide insights"""
        
        prompt = f"""
Analyze these repository metrics and provide insights.

Metrics:
{json.dumps(metrics, indent=2)}

Provide analysis on:
1. Development activity trends
2. Code quality indicators
3. Community engagement
4. Project health assessment
5. Performance metrics
6. Growth patterns
7. Risk factors
8. Recommendations for improvement

Present insights in a clear, actionable format.
"""
        
        result = await self._generate_with_thinking(
            prompt=prompt,
            thinking_budget=1200
        )
        
        return result.get("content", "")
