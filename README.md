# Online Examination System (Jenkins CI/CD Enabled)

A robust examination portal integrated with a Jenkins Declarative Pipeline for continuous integration and automated testing.

## Jenkins Pipeline Stages
1. **Checkout**: Pull latest code from Git.
2. **Environment & Setup**: Validate Python runtime.
3. **Code Quality & Lint**: Syntax compilation check.
4. **Automated Unit Tests**: Execute 	est_system.py suite.
5. **Build & Package**: Create release zip archive.
6. **Deploy / Release**: Production deployment for main branch.

## System Modules
- Jenkinsfile: Declarative Jenkins pipeline script.
- config.py: Core system settings and exam configurations.
- questions.py: Question bank management.
- scoring.py: Automated grading engine.
- uth.py: Student authentication with @vitapstudent.ac.in domain validation.
- pp.py: Interactive web portal.
- 	est_system.py: Automated test suite for Jenkins CI.
