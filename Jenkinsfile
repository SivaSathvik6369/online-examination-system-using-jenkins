pipeline {
    agent any

    environment {
        SYSTEM_NAME = 'Online Examination System'
        DOCKER_IMAGE = 'online-examination-system'
        DOCKER_TAG = 'latest'
        K8S_CLUSTER = 'k8s-lab6'
        DEPLOYMENT_NAME = 'online-exam-deployment'
        SERVICE_NAME = 'online-exam-service'
        NODEPORT = '30080'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Pulling latest source code from GitHub repository...'
                checkout scm
            }
        }

        stage('Environment & Toolchain') {
            steps {
                echo 'Validating Python, Docker, and Kubernetes (kubectl) toolchains...'
                bat 'python --version'
                bat 'docker --version'
                bat 'kubectl version --client'
                bat 'kubectl get nodes'
            }
        }

        stage('Code Quality & Automated Testing') {
            steps {
                echo 'Running unit test suite...'
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

        stage('Kubernetes Cluster Deployment') {
            steps {
                echo 'Loading container image into Kubernetes cluster nodes...'
                bat "kind load docker-image %DOCKER_IMAGE%:%DOCKER_TAG% --name %K8S_CLUSTER%"
                echo 'Applying Kubernetes Deployment and Service manifests...'
                bat 'kubectl apply -f k8s/deployment.yaml'
                bat 'kubectl apply -f k8s/service.yaml'
                bat 'kubectl rollout status deployment/%DEPLOYMENT_NAME%'
            }
        }

        stage('Replica Scaling & Self-Healing') {
            steps {
                echo 'Scaling deployment replicas to 4 pods for high availability...'
                bat 'kubectl scale deployment %DEPLOYMENT_NAME% --replicas=4'
                bat 'kubectl get pods -l app=online-exam'
            }
        }

        stage('Cluster Health & Verification') {
            steps {
                echo 'Verifying Kubernetes NodePort service endpoint...'
                bat 'kubectl get svc %SERVICE_NAME%'
                bat "curl.exe -I http://localhost:%NODEPORT%/"
                echo 'SUCCESS: Online Examination System is LIVE on Kubernetes at http://localhost:30080'
            }
        }
    }

    post {
        always {
            echo 'Lab 6 Pipeline execution complete.'
        }
        success {
            echo 'SUCCESS: Automated CI/CD, Containerization, and Kubernetes Orchestration finished with STABLE status.'
        }
        failure {
            echo 'FAILURE: Pipeline execution failed! Check pod events and container logs.'
        }
    }
}
