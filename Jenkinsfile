pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Kodni GitHub-dan yuklab olish muvaffaqiyatli bajarildi!'
            }
        }
        stage('Build') {
            steps {
                echo 'Loyiha yig\'ilmoqda (Build)...'
                // Loyihangiz turiga qarab buyruq kiritiladi (masalan: sh 'npm install' yoki sh './gradlew build')
            }
        }
        stage('Test') {
            steps {
                echo 'Testlar bajarilmoqda...'
            }
        }
    }
}
