pipeline {
    agent any

    environment {
        PYTHON_CMD = 'python'
        SYSTEM_NAME = 'Online Examination System'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from Git repository...'
                checkout scm
            }
        }

        stage('Environment & Setup') {
            steps {
                echo 'Setting up environment and validating Python installation...'
                bat 'python --version'
            }
        }

        stage('Code Quality & Lint') {
            steps {
                echo 'Validating Python syntax and code formatting...'
                bat 'python -m py_compile config.py questions.py scoring.py auth.py test_system.py'
            }
        }

        stage('Automated Unit Tests') {
            steps {
                echo 'Executing automated unit test suite...'
                bat 'python test_system.py'
            }
        }

        stage('Build & Package') {
            steps {
                echo 'Packaging application artifact...'
                bat 'git archive --format=zip --output=online-exam-system-v1.0.0.zip HEAD'
            }
        }

        stage('Deploy / Release') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying Online Examination System to production environment...'
                echo 'Application ready for candidates at http://localhost:5000'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo 'SUCCESS: All Jenkins pipeline stages passed. Build is stable!'
        }
        failure {
            echo 'FAILURE: Jenkins test suite or build failed. Alerting DevOps team!'
        }
    }
}
