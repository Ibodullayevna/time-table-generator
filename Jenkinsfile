pipeline {
    agent any

    environment {
        // Docker Hub login va image nomi
        DOCKER_USER = 'Ibodullayevna'
        IMAGE_NAME  = 'time-table-generator'
        
        // Jenkins'dagi credential ID
        DOCKERHUB_CRED = credentials('docker-hub-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Docker image yig\'ilmoqda...'
                    sh "docker build -t ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_NUMBER} ."
                    sh "docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo 'Docker Hub\'ga yuklanmoqda...'
                    sh "echo \$DOCKERHUB_CRED_PSW | docker login -u \$DOCKERHUB_CRED_USR --password-stdin"
                    sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:latest"
                }
            }
        }
    }
}
