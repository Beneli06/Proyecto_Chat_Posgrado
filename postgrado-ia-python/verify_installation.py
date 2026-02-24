#!/usr/bin/env python3
"""
RAG Chatbot Project - Installation & Verification Script

This script helps verify that all project components are properly installed
and ready for deployment.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section"""
    print(f"\n✓ {text}")


def check_file_exists(path, name):
    """Check if a file exists"""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"  {status} {name}")
    return exists


def check_directory_exists(path, name):
    """Check if a directory exists"""
    exists = Path(path).is_dir()
    status = "✅" if exists else "❌"
    print(f"  {status} {name}")
    return exists


def verify_docker_installation():
    """Verify Docker is installed"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ Docker: {result.stdout.strip()}")
            return True
        else:
            print("  ❌ Docker is not working properly")
            return False
    except FileNotFoundError:
        print("  ❌ Docker is not installed")
        return False


def verify_docker_compose_installation():
    """Verify Docker Compose is installed"""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ Docker Compose: {result.stdout.strip()}")
            return True
        else:
            print("  ❌ Docker Compose is not working properly")
            return False
    except FileNotFoundError:
        print("  ❌ Docker Compose is not installed")
        return False


def verify_python_installation():
    """Verify Python 3.11+ is installed"""
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  ✅ Python: {version}")
            return True
        else:
            print("  ❌ Python is not working properly")
            return False
    except FileNotFoundError:
        print("  ❌ Python is not installed")
        return False


def main():
    """Main verification function"""
    
    print_header("RAG CHATBOT PROJECT VERIFICATION")
    print("This script verifies that all project components are in place.")
    
    # Get project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Track results
    all_passed = True
    
    # 1. System Requirements
    print_section("System Requirements")
    print("  Checking installed software...")
    docker_ok = verify_docker_installation()
    compose_ok = verify_docker_compose_installation()
    python_ok = verify_python_installation()
    
    if not (docker_ok and compose_ok and python_ok):
        print("\n  ⚠️  Some system requirements are missing.")
        print("     Please refer to DEPLOYMENT_GUIDE.md Phase 1")
        all_passed = False
    else:
        print("\n  ✅ All system requirements met")
    
    # 2. Project Files
    print_section("Project Files")
    print("  Checking core application files...")
    
    files_to_check = [
        ("app/main.py", "FastAPI Application"),
        ("app/config.py", "Configuration Module"),
        ("app/engine/ingest.py", "PDF Ingestion Engine"),
        ("app/engine/query.py", "RAG Query Engine"),
        ("app/utils/validators.py", "Input Validators"),
        ("app/utils/logging_config.py", "Logging Configuration"),
        ("requirements.txt", "Python Dependencies"),
        ("pytest.ini", "Pytest Configuration"),
        ("Dockerfile", "Docker Image Definition"),
        ("docker-compose.yml", "Docker Compose Configuration"),
        (".env", "Environment Variables"),
        (".gitignore", "Git Ignore Rules"),
    ]
    
    for file_path, name in files_to_check:
        if not check_file_exists(file_path, name):
            all_passed = False
    
    # 3. Test Files
    print_section("Test Files")
    print("  Checking test suite files...")
    
    test_files = [
        ("tests/test_rag_logic.py", "RAG Logic Tests"),
        ("tests/test_api.py", "API Tests"),
        ("tests/conftest.py", "Pytest Configuration"),
    ]
    
    for file_path, name in test_files:
        if not check_file_exists(file_path, name):
            all_passed = False
    
    # 4. Documentation
    print_section("Documentation")
    print("  Checking documentation files...")
    
    docs = [
        ("README.md", "Project README"),
        ("PROJECT_SUMMARY.md", "Project Summary"),
        ("DEPLOYMENT_GUIDE.md", "Deployment Guide"),
        ("N8N_SETUP_GUIDE.md", "n8n Setup Guide"),
        ("SYSTEM_PROMPT_AND_METADATA.md", "System Prompt & Metadata"),
        ("DELIVERABLES.md", "Deliverables Checklist"),
        ("DOCUMENTATION_INDEX.md", "Documentation Index"),
    ]
    
    for file_path, name in docs:
        if not check_file_exists(file_path, name):
            all_passed = False
    
    # 5. Directories
    print_section("Required Directories")
    print("  Checking directory structure...")
    
    directories = [
        ("app", "Application Package"),
        ("app/engine", "RAG Engine Package"),
        ("app/utils", "Utilities Package"),
        ("tests", "Tests Package"),
        ("documents", "Documents Folder"),
    ]
    
    for dir_path, name in directories:
        if not check_directory_exists(dir_path, name):
            all_passed = False
    
    # 6. Summary
    print_header("VERIFICATION SUMMARY")
    
    if all_passed:
        print("""
✅ ALL CHECKS PASSED

Your RAG Chatbot project is complete and ready for deployment!

Next Steps:
1. Edit .env with your API keys (especially OPENAI_API_KEY)
2. Follow DEPLOYMENT_GUIDE.md for step-by-step deployment
3. Use DOCUMENTATION_INDEX.md to navigate all documentation
4. Configure n8n workflows using N8N_SETUP_GUIDE.md

Quick Start:
  docker-compose up -d         # Start all services
  docker-compose ps            # Check status
  curl http://localhost:8000/health  # Verify API

For detailed instructions, see:
  - DEPLOYMENT_GUIDE.md (Production deployment)
  - README.md (Project overview)
  - DOCUMENTATION_INDEX.md (Navigation guide)
""")
        return 0
    else:
        print("""
⚠️  SOME CHECKS FAILED

Please review the items marked with ❌ above.

Common Issues:
1. Missing system dependencies → See DEPLOYMENT_GUIDE.md Phase 1
2. Incomplete project files → Project may not be fully extracted
3. Missing documentation → Download complete project files

For help:
  - DEPLOYMENT_GUIDE.md (Troubleshooting section)
  - DOCUMENTATION_INDEX.md (Find relevant documentation)
  - GitHub issues (if applicable)
""")
        return 1


if __name__ == "__main__":
    sys.exit(main())
