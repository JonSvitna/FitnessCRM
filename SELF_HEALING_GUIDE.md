# Self-Healing & Continuous Monitoring Guide

Complete guide for implementing self-healing capabilities and continuous monitoring in FitnessCRM using the AI Orchestrator.

## 🎯 Overview

The AI Orchestrator provides self-healing capabilities through:
1. **Automated Error Detection**: Identifies errors and exceptions
2. **Root Cause Analysis**: Uses AI to analyze errors
3. **Suggested Fixes**: Generates code fixes automatically
4. **Health Monitoring**: Continuous system health checks
5. **Proactive Alerts**: Notifies team of issues

## 🔧 Components

### 1. Error Detection System

**Purpose**: Automatically capture and log all application errors

**Implementation**:

```python
# backend/utils/error_handler.py
import traceback
import requests
from utils.logger import logger
from datetime import datetime
import os

AI_ORCHESTRATOR_URL = os.getenv('AI_ORCHESTRATOR_URL')

def analyze_error_with_ai(error_data):
    """Send error to AI orchestrator for analysis"""
    try:
        response = requests.post(
            f"{AI_ORCHESTRATOR_URL}/api/execute",
            json={
                "task_type": "code_analysis",
                "input_data": {
                    "error": str(error_data['error']),
                    "stack_trace": error_data['stack_trace'],
                    "context": error_data['context'],
                    "timestamp": error_data['timestamp']
                }
            },
            timeout=10  # Quick timeout for error handling
        )
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to analyze error with AI: {str(e)}")
    
    return None

def get_request_context():
    """Get relevant request context"""
    from flask import request
    return {
        'url': request.url if request else None,
        'method': request.method if request else None,
        'headers': dict(request.headers) if request else None,
        'remote_addr': request.remote_addr if request else None
    }

class ErrorHandler:
    """Central error handling with AI analysis"""
    
    @staticmethod
    def handle_exception(e, context=None):
        """Handle exception with AI analysis"""
        error_data = {
            'error': str(e),
            'type': type(e).__name__,
            'stack_trace': traceback.format_exc(),
            'context': context or get_request_context(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log error
        logger.error(f"Exception occurred: {error_data['error']}", exc_info=True)
        
        # Analyze with AI (async, don't block)
        try:
            analysis = analyze_error_with_ai(error_data)
            if analysis:
                logger.info(f"AI Analysis: {analysis}")
                # Store analysis for review
                from models.error_log import ErrorLog
                ErrorLog.create_with_analysis(error_data, analysis)
        except Exception as analysis_error:
            logger.error(f"Error during AI analysis: {str(analysis_error)}")
        
        return error_data

# Integrate with Flask
def init_error_handling(app):
    """Initialize error handling for Flask app"""
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        error_data = ErrorHandler.handle_exception(e)
        
        # Return appropriate response
        from flask import jsonify
        return jsonify({
            'error': 'An error occurred',
            'message': str(e),
            'timestamp': error_data['timestamp']
        }), 500
    
    @app.errorhandler(404)
    def handle_404(e):
        from flask import jsonify
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(400)
    def handle_400(e):
        from flask import jsonify
        return jsonify({'error': 'Bad request'}), 400
```

**Add to app.py**:
```python
from utils.error_handler import init_error_handling

def create_app(config_name=None):
    # ... existing code ...
    
    # Initialize error handling
    init_error_handling(app)
    
    return app
```

---

### 2. Health Monitoring System

**Purpose**: Continuous monitoring of system components

**Implementation**:

```python
# backend/utils/health_monitor.py
import schedule
import time
from threading import Thread
import requests
import os
from utils.logger import logger
from datetime import datetime

AI_ORCHESTRATOR_URL = os.getenv('AI_ORCHESTRATOR_URL')

class HealthMonitor:
    """Continuous health monitoring"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start health monitoring"""
        if self.running:
            return
        
        self.running = True
        
        # Schedule checks
        schedule.every(5).minutes.do(self.check_system_health)
        schedule.every(15).minutes.do(self.check_database_health)
        schedule.every(30).minutes.do(self.check_api_health)
        
        # Start scheduler thread
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Health monitoring started")
    
    def stop(self):
        """Stop health monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _run_scheduler(self):
        """Run scheduled tasks"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def check_system_health(self):
        """Check overall system health"""
        try:
            response = requests.post(
                f"{AI_ORCHESTRATOR_URL}/api/execute",
                json={
                    "task_type": "health_check",
                    "input_data": {
                        "timestamp": datetime.utcnow().isoformat()
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self._process_health_result(result)
            else:
                logger.warning(f"Health check returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
    
    def check_database_health(self):
        """Check database connectivity and performance"""
        from models import db
        try:
            start = time.time()
            db.session.execute(db.text('SELECT 1'))
            duration = time.time() - start
            
            if duration > 1.0:
                logger.warning(f"Database query slow: {duration:.2f}s")
                self._send_alert("Database performance degraded")
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            self._send_alert("Database connection failed", "critical")
    
    def check_api_health(self):
        """Check API endpoints health"""
        from flask import current_app
        try:
            with current_app.test_client() as client:
                response = client.get('/api/health')
                if response.status_code != 200:
                    logger.warning(f"API health check failed: {response.status_code}")
                    self._send_alert("API health check failed")
                    
        except Exception as e:
            logger.error(f"API health check failed: {str(e)}")
    
    def _process_health_result(self, result):
        """Process health check result"""
        if not result.get('success'):
            logger.error(f"Health check failed: {result.get('error')}")
            return
        
        health_checks = result.get('results', {}).get('health_checks', [])
        
        for check in health_checks:
            status = check.get('status')
            component = check.get('component')
            message = check.get('message')
            
            if status == 'critical':
                logger.error(f"CRITICAL: {component} - {message}")
                self._send_alert(f"Critical issue in {component}: {message}", "critical")
            elif status == 'warning':
                logger.warning(f"WARNING: {component} - {message}")
                self._send_alert(f"Warning in {component}: {message}", "warning")
            else:
                logger.info(f"OK: {component} - {message}")
    
    def _send_alert(self, message, severity="warning"):
        """Send alert notification"""
        # TODO: Implement actual alerting (email, Slack, etc.)
        logger.warning(f"ALERT [{severity}]: {message}")
        
        # Could send to:
        # - Email via SendGrid
        # - Slack webhook
        # - SMS via Twilio
        # - PagerDuty for critical alerts

# Global instance
health_monitor = HealthMonitor()

def start_health_monitoring():
    """Start health monitoring (call from app startup)"""
    health_monitor.start()

def stop_health_monitoring():
    """Stop health monitoring"""
    health_monitor.stop()
```

**Add to app.py**:
```python
from utils.health_monitor import start_health_monitoring

def create_app(config_name=None):
    # ... existing code ...
    
    # Start health monitoring
    if os.getenv('ENABLE_HEALTH_MONITORING', 'true').lower() == 'true':
        start_health_monitoring()
    
    return app
```

---

### 3. Automated Code Review

**Purpose**: Review code changes before deployment

**Implementation**:

```yaml
# .github/workflows/ai-code-review.yml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch all history for comparison
      
      - name: Get changed files
        id: changed-files
        run: |
          echo "files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | grep -E '\.(py|js)$' | tr '\n' ' ')" >> $GITHUB_OUTPUT
      
      - name: Review changed files
        env:
          AI_ORCHESTRATOR_URL: ${{ secrets.AI_ORCHESTRATOR_URL }}
          AI_ORCHESTRATOR_KEY: ${{ secrets.AI_ORCHESTRATOR_KEY }}
        run: |
          FILES="${{ steps.changed-files.outputs.files }}"
          
          for FILE in $FILES; do
            if [ -f "$FILE" ]; then
              echo "Reviewing: $FILE"
              
              CODE=$(cat "$FILE")
              
              RESPONSE=$(curl -s -X POST "$AI_ORCHESTRATOR_URL/api/execute" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $AI_ORCHESTRATOR_KEY" \
                -d "{
                  \"task_type\": \"code_analysis\",
                  \"input_data\": {
                    \"code\": $(echo "$CODE" | jq -Rs .),
                    \"file_path\": \"$FILE\",
                    \"analysis_type\": \"comprehensive\"
                  }
                }")
              
              echo "$RESPONSE" >> review-results.json
            fi
          done
      
      - name: Post review comments
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            
            if (!fs.existsSync('review-results.json')) {
              console.log('No review results found');
              return;
            }
            
            const results = JSON.parse(fs.readFileSync('review-results.json', 'utf8'));
            
            // Post as PR comment
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## AI Code Review\n\n' + JSON.stringify(results, null, 2)
            });
```

---

### 4. Self-Healing Actions

**Purpose**: Automatically apply fixes for known issues

**Implementation**:

```python
# backend/utils/self_healer.py
import os
import subprocess
from utils.logger import logger
from models.agent import CodeSuggestion

class SelfHealer:
    """Automated fix application"""
    
    @staticmethod
    def can_auto_fix(suggestion):
        """Determine if suggestion can be automatically applied"""
        # Only auto-fix low severity issues
        if suggestion.severity not in ['low', 'medium']:
            return False
        
        # Only auto-fix certain types
        safe_types = ['style', 'formatting', 'import_optimization']
        if suggestion.issue_type not in safe_types:
            return False
        
        return True
    
    @staticmethod
    def apply_fix(suggestion):
        """Apply suggested fix"""
        if not SelfHealer.can_auto_fix(suggestion):
            logger.warning(f"Cannot auto-fix suggestion {suggestion.id}: safety check failed")
            return False
        
        try:
            # Parse file and apply fix
            # This is a simplified example - real implementation would be more robust
            file_path = suggestion.file_path
            
            # Backup original file
            SelfHealer._backup_file(file_path)
            
            # Apply fix (implementation depends on fix type)
            # Could use AST manipulation, regex, or other tools
            
            # Verify fix didn't break anything
            if SelfHealer._verify_fix(file_path):
                logger.info(f"Successfully applied fix for suggestion {suggestion.id}")
                suggestion.status = 'applied'
                suggestion.save()
                return True
            else:
                # Rollback
                SelfHealer._restore_backup(file_path)
                logger.warning(f"Fix verification failed for suggestion {suggestion.id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply fix: {str(e)}")
            SelfHealer._restore_backup(file_path)
            return False
    
    @staticmethod
    def _backup_file(file_path):
        """Backup file before modification"""
        import shutil
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)
    
    @staticmethod
    def _restore_backup(file_path):
        """Restore file from backup"""
        import shutil
        backup_path = f"{file_path}.backup"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
    
    @staticmethod
    def _verify_fix(file_path):
        """Verify fix didn't break anything"""
        # Run linter
        try:
            if file_path.endswith('.py'):
                result = subprocess.run(
                    ['python', '-m', 'py_compile', file_path],
                    capture_output=True,
                    timeout=10
                )
                return result.returncode == 0
            elif file_path.endswith('.js'):
                # Could use eslint or similar
                return True
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return False
        
        return True
```

---

## 📊 Monitoring Dashboard

Access the monitoring dashboard at:
- Local: `http://localhost:5001/gui`
- Production: `https://your-orchestrator.up.railway.app/gui`

**Features**:
- Real-time agent status
- Execution history
- System health indicators
- Code suggestions review
- One-click fix application

---

## 🚨 Alerting Configuration

### Email Alerts

```python
# backend/utils/alerts.py
from flask_mail import Message
from utils.email import mail

def send_alert_email(subject, body, severity="warning"):
    """Send alert email"""
    admin_emails = os.getenv('ADMIN_EMAILS', '').split(',')
    
    if not admin_emails:
        return
    
    msg = Message(
        subject=f"[{severity.upper()}] {subject}",
        recipients=admin_emails,
        body=body
    )
    
    mail.send(msg)
```

### Slack Alerts

```python
# backend/utils/alerts.py
import requests

def send_slack_alert(message, severity="warning"):
    """Send alert to Slack"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        return
    
    color = {
        'info': '#36a64f',
        'warning': '#ff9900',
        'critical': '#ff0000'
    }.get(severity, '#808080')
    
    payload = {
        'attachments': [{
            'color': color,
            'title': f'{severity.upper()} Alert',
            'text': message,
            'footer': 'FitnessCRM Monitoring',
            'ts': int(time.time())
        }]
    }
    
    requests.post(webhook_url, json=payload)
```

---

## 🔄 Continuous Improvement Loop

1. **Error Occurs** → Captured by error handler
2. **AI Analysis** → Root cause identified
3. **Fix Generated** → AI suggests code fix
4. **Review** → Human or automated review
5. **Apply** → Fix applied and verified
6. **Learn** → Pattern added to knowledge base
7. **Prevent** → Similar errors avoided in future

---

## 📈 Metrics to Track

- **MTTR** (Mean Time To Recovery): Average time to fix issues
- **Error Rate**: Errors per hour/day
- **Fix Success Rate**: Percentage of successful auto-fixes
- **False Positive Rate**: Incorrect AI suggestions
- **System Uptime**: Overall availability
- **Response Time**: API response times

---

## 🎯 Best Practices

1. **Start Conservative**: Only auto-fix low-risk issues
2. **Always Backup**: Backup before applying fixes
3. **Verify Everything**: Test fixes before committing
4. **Human Review**: Keep humans in the loop for critical issues
5. **Monitor Costs**: Track OpenAI API usage
6. **Log Everything**: Comprehensive logging for debugging
7. **Gradual Rollout**: Test in dev before production

---

## 🔐 Security Considerations

- **Code Execution**: Be very careful with automated code execution
- **Access Control**: Limit who can approve auto-fixes
- **Audit Trail**: Log all automated changes
- **Rollback Plan**: Always have a way to undo changes
- **Testing**: Automated testing before deployment

---

## 📚 Additional Resources

- [AI Orchestrator README](ai-orchestrator/README.md)
- [Health Check Agent Documentation](ai-orchestrator/agents/health_checker.py)
- [Code Analyzer Agent Documentation](ai-orchestrator/agents/code_analyzer.py)
- [Error Handling Best Practices](https://flask.palletsprojects.com/en/2.3.x/errorhandling/)
