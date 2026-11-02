pipeline {
    agent any

    environment {
        SYSTEM_NAME = 'Online Examination System'
        DOCKER_IMAGE = 'online-examination-system'
        DOCKER_TAG = 'latest'
        CONTAINER_NAME = 'online-exam-container'
        APP_PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling latest source code from GitHub repository...'
                checkout scm
            }
        }

        stage('Environment & Setup') {
            steps {
                echo 'Checking Python and Docker runtime environments...'
                bat 'python --version'
                bat 'docker --version'
            }
        }

        stage('Code Quality & Automated Testing') {
            steps {
                echo 'Executing automated unit test suite...'
                bat 'python test_system.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building container image using Dockerfile...'
                bat "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% ."
                echo 'Docker container image created successfully.'
            }
        }

        stage('Deploy Docker Container') {
            steps {
                echo 'Deploying container application on Docker Desktop...'
                bat "docker stop %CONTAINER_NAME% || exit 0"
                bat "docker rm %CONTAINER_NAME% || exit 0"
                bat "docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:5000 %DOCKER_IMAGE%:%DOCKER_TAG%"
                echo 'Application deployed successfully inside Docker container.'
            }
        }

        stage('Health Check & Verification') {
            steps {
                echo 'Verifying container health status and live web endpoint...'
                bat "docker ps --filter name=%CONTAINER_NAME%"
                bat "curl.exe -I http://localhost:%APP_PORT%/"
                echo 'SUCCESS: Online Examination System is LIVE and healthy on http://localhost:5000'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo 'SUCCESS: Continuous Integration and Continuous Deployment finished with STABLE status.'
        }
        failure {
            echo 'FAILURE: Pipeline execution failed! Check build and container logs.'
        }
    }
}
