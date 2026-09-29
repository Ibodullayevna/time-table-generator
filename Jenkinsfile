pipeline {
    agent any

    environment {
        DOCKER_USER = 'Ibodullayevna'
        IMAGE_NAME  = 'time-table-generator'
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
                    echo "Docker image yig'ilmoqda..."
                    sh "docker build -t ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_NUMBER} ."
                    sh "docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest ."
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    script {
                        echo "Docker Hub'ga yuklanmoqda..."
                        sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
                        sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:${BUILD_NUMBER}"
                        sh "docker push ${DOCKER_USER}/${IMAGE_NAME}:latest"
                    }
                }
            }
        }
    }
}
