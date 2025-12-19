"""
Code Analyzer Agent
Analyzes code quality, identifies bugs, and suggests improvements
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent
from models import db
from models.agent import CodeSuggestion
from datetime import datetime
import os


class CodeAnalyzerAgent(BaseAgent):
    """Agent for code analysis and improvement suggestions"""
    
    def __init__(self, agent_id: int, name: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, config)
        self.llm = ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=self.get_config_value('model', 'gpt-4-turbo-preview'),
            temperature=self.get_config_value('temperature', 0.3)  # Lower temp for code analysis
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code analysis
        
        Args:
            input_data: Must contain:
                - code: Code snippet or file content to analyze
                - file_path: Path to the file (optional)
                - analysis_type: Type of analysis (bug, performance, security, style)
        
        Returns:
            Code analysis results and suggestions
        """
        # Validate input
        if not self.validate_input(input_data, ['code']):
            raise ValueError("code is required")
        
        code = input_data['code']
        file_path = input_data.get('file_path', 'unknown')
        analysis_type = input_data.get('analysis_type', 'comprehensive')
        
        # Create prompt for LLM
        system_prompt = """You are an expert software engineer AI specializing in code review and quality analysis.
Your role is to identify bugs, security issues, performance problems, and style improvements in code.
Provide specific, actionable recommendations with code examples."""
        
        user_prompt = f"""Analyze the following code for {analysis_type} issues:

File: {file_path}

Code:
```
{code}
```

Please provide:
1. Identified Issues (categorized by severity: critical, high, medium, low)
2. Detailed Explanation of each issue
3. Specific Code Fixes or Improvements
4. Best Practice Recommendations
5. Security Considerations

Format the response as a structured JSON array of issues."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Get LLM response
        response = self.llm.invoke(messages)
        
        # Parse and store suggestions
        suggestions = self._parse_and_store_suggestions(
            response.content,
            file_path,
            code
        )
        
        return {
            'file_path': file_path,
            'analysis_type': analysis_type,
            'analysis_result': response.content,
            'suggestions_created': len(suggestions),
            'suggestion_ids': [s.id for s in suggestions]
        }
    
    def _parse_and_store_suggestions(
        self,
        analysis_result: str,
        file_path: str,
        code_snippet: str
    ) -> List[CodeSuggestion]:
        """
        Parse analysis result and store as code suggestions
        
        Args:
            analysis_result: LLM analysis output
            file_path: File being analyzed
            code_snippet: Original code
        
        Returns:
            List of created CodeSuggestion objects
        """
        suggestions = []
        
        try:
            # Try to parse JSON response
            import json
            issues = json.loads(analysis_result)
            
            if not isinstance(issues, list):
                issues = [issues]
            
            for issue in issues:
                suggestion = CodeSuggestion(
                    file_path=file_path,
                    issue_type=issue.get('type', 'general'),
                    severity=issue.get('severity', 'medium'),
                    description=issue.get('description', 'No description'),
                    suggestion=issue.get('fix', 'See analysis'),
                    code_snippet=code_snippet[:500],  # Limit size
                    status='pending',
                    created_at=datetime.utcnow()
                )
                db.session.add(suggestion)
                suggestions.append(suggestion)
            
            db.session.commit()
            
        except json.JSONDecodeError:
            # If not JSON, create single suggestion with full text
            suggestion = CodeSuggestion(
                file_path=file_path,
                issue_type='general',
                severity='medium',
                description='Code analysis completed',
                suggestion=analysis_result[:1000],  # Limit size
                code_snippet=code_snippet[:500],
                status='pending',
                created_at=datetime.utcnow()
            )
            db.session.add(suggestion)
            db.session.commit()
            suggestions.append(suggestion)
        
        return suggestions
    
    async def analyze_error_log(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze error logs and suggest fixes
        
        Args:
            error_data: Error log data including stack trace
        
        Returns:
            Analysis and fix suggestions
        """
        error_message = error_data.get('error', '')
        stack_trace = error_data.get('stack_trace', '')
        context = error_data.get('context', {})
        
        system_prompt = """You are an expert debugging AI that analyzes errors and provides solutions.
Your role is to understand error messages, identify root causes, and suggest specific fixes."""
        
        user_prompt = f"""Analyze this error and provide a fix:

Error: {error_message}

Stack Trace:
{stack_trace}

Context: {context}

Please provide:
1. Root Cause Analysis
2. Specific Fix (with code if applicable)
3. Prevention Strategies
4. Related Issues to Check

Format as JSON."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            'error_analysis': response.content,
            'timestamp': datetime.utcnow().isoformat()
        }
