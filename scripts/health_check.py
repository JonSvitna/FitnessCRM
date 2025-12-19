#!/usr/bin/env python3
"""
System Health Check Script for FitnessCRM

This script performs comprehensive health checks on all system components
including the database, API, external services, and system resources.
"""

import os
import sys
import time
import requests
import psycopg2
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class HealthChecker:
    """System health checker."""
    
    def __init__(self, api_url=None, db_url=None):
        self.api_url = api_url or os.environ.get('VITE_API_URL', 'http://localhost:5000')
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        self.results = []
        
    def log(self, status, component, message):
        """Log a health check result."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status_color = GREEN if status == 'PASS' else RED if status == 'FAIL' else YELLOW
        print(f"[{timestamp}] {status_color}{status:6s}{RESET} | {component:20s} | {message}")
        self.results.append({
            'timestamp': timestamp,
            'status': status,
            'component': component,
            'message': message
        })
        
    def check_api_health(self):
        """Check API health endpoint."""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log('PASS', 'API Health', f"API is healthy - {data.get('status', 'unknown')}")
                return True
            else:
                self.log('FAIL', 'API Health', f"API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log('FAIL', 'API Health', "Cannot connect to API")
            return False
        except Exception as e:
            self.log('FAIL', 'API Health', f"Error: {str(e)}")
            return False
            
    def check_database(self):
        """Check database connectivity."""
        if not self.db_url:
            self.log('WARN', 'Database', "DATABASE_URL not configured")
            return False
            
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            self.log('PASS', 'Database', f"Connected successfully - {version.split()[0]}")
            return True
        except Exception as e:
            self.log('FAIL', 'Database', f"Connection failed: {str(e)}")
            return False
            
    def check_database_tables(self):
        """Check if required database tables exist."""
        if not self.db_url:
            self.log('WARN', 'Database Tables', "DATABASE_URL not configured")
            return False
            
        required_tables = [
            'trainers', 'clients', 'assignments', 'sessions',
            'progress_records', 'payments', 'workout_plans'
        ]
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            cursor.close()
            conn.close()
            
            if not missing_tables:
                self.log('PASS', 'Database Tables', f"All {len(required_tables)} required tables exist")
                return True
            else:
                self.log('FAIL', 'Database Tables', f"Missing tables: {', '.join(missing_tables)}")
                return False
        except Exception as e:
            self.log('FAIL', 'Database Tables', f"Error: {str(e)}")
            return False
            
    def check_api_endpoints(self):
        """Check critical API endpoints.
        
        Note: 401/403 responses are considered acceptable as they indicate
        the endpoint exists and authentication/authorization is properly enforced.
        If these endpoints should be publicly accessible, update this check.
        """
        endpoints = [
            '/api/trainers',
            '/api/clients',
            '/api/crm/dashboard',
            '/api/sessions'
        ]
        
        all_pass = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log('PASS', 'API Endpoint', f"{endpoint} is accessible (200 OK)")
                elif response.status_code in [401, 403]:
                    # Auth required - endpoint exists and is protected
                    self.log('PASS', 'API Endpoint', f"{endpoint} is protected ({response.status_code})")
                else:
                    self.log('FAIL', 'API Endpoint', f"{endpoint} returned {response.status_code}")
                    all_pass = False
            except Exception as e:
                self.log('FAIL', 'API Endpoint', f"{endpoint} - {str(e)}")
                all_pass = False
                
        return all_pass
        
    def check_environment_variables(self):
        """Check if required environment variables are set."""
        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY'
        ]
        
        optional_vars = [
            'MAIL_SERVER',
            'TWILIO_ACCOUNT_SID',
            'STRIPE_SECRET_KEY'
        ]
        
        all_set = True
        for var in required_vars:
            if os.environ.get(var):
                self.log('PASS', 'Environment', f"{var} is configured")
            else:
                self.log('FAIL', 'Environment', f"{var} is NOT configured")
                all_set = False
                
        for var in optional_vars:
            if os.environ.get(var):
                self.log('PASS', 'Environment', f"{var} is configured (optional)")
            else:
                self.log('WARN', 'Environment', f"{var} is NOT configured (optional)")
                
        return all_set
        
    def check_disk_space(self):
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_percent = (free / total) * 100
            
            if free_percent > 20:
                self.log('PASS', 'Disk Space', f"{free_percent:.1f}% free ({free // (2**30)} GB)")
                return True
            elif free_percent > 10:
                self.log('WARN', 'Disk Space', f"{free_percent:.1f}% free ({free // (2**30)} GB)")
                return True
            else:
                self.log('FAIL', 'Disk Space', f"Low disk space: {free_percent:.1f}% free")
                return False
        except Exception as e:
            self.log('WARN', 'Disk Space', f"Cannot check disk space: {str(e)}")
            return True
            
    def run_all_checks(self):
        """Run all health checks."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}FitnessCRM System Health Check{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        checks = [
            ('Environment Variables', self.check_environment_variables),
            ('API Health', self.check_api_health),
            ('Database Connection', self.check_database),
            ('Database Tables', self.check_database_tables),
            ('API Endpoints', self.check_api_endpoints),
            ('Disk Space', self.check_disk_space)
        ]
        
        results = {}
        for name, check_func in checks:
            try:
                results[name] = check_func()
            except Exception as e:
                self.log('FAIL', name, f"Unexpected error: {str(e)}")
                results[name] = False
                
        # Summary
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}Summary{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        failed = total - passed
        
        print(f"Total Checks: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        
        if failed == 0:
            print(f"\n{GREEN}✓ All health checks passed!{RESET}\n")
            return 0
        else:
            print(f"\n{RED}✗ {failed} health check(s) failed{RESET}\n")
            return 1


def main():
    """Main entry point."""
    checker = HealthChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
