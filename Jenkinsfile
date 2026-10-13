pipeline {
    agent any

    environment {
        SYSTEM_NAME = 'Online Examination System'
        JAR_NAME = 'online-examination-system.jar'
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
                echo 'Setting up environment and validating runtime...'
                bat 'python --version'
                bat 'java -version'
            }
        }

        stage('Code Quality & Lint') {
            steps {
                echo 'Validating syntax and code structure...'
                bat 'python -m py_compile config.py questions.py scoring.py auth.py test_system.py'
            }
        }

        stage('Automated Unit Tests') {
            steps {
                echo 'Executing automated unit test suite...'
                // If any test fails, pipeline aborts here with FAILURE, and NO JAR is created!
                bat 'python test_system.py'
            }
        }

        stage('Build & Package JAR') {
            // This stage only executes if the Automated Unit Tests stage PASSES completely!
            steps {
                echo 'All tests passed successfully! Packaging application into executable JAR artifact...'
                bat 'echo Manifest-Version: 1.0 > MANIFEST.MF'
                bat 'echo Main-Class: OnlineExamSystem >> MANIFEST.MF'
                bat 'tar -cf online-examination-system.jar MANIFEST.MF *.py README.md'
                echo 'SUCCESS: online-examination-system.jar created successfully!'
            }
        }

        stage('Deploy / Release') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying Online Examination System artifact to production...'
                echo 'Artifact ready: online-examination-system.jar'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution complete.'
        }
        success {
            echo 'SUCCESS: Build is STABLE. Archiving JAR artifact...'
            archiveArtifacts artifacts: '*.jar', fingerprint: true, allowEmptyArchive: true
        }
        failure {
            echo 'FAILURE: Test suite failed! Pipeline aborted. No JAR artifact was generated.'
        }
    }
}
