```groovy
pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    options {
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                    if not exist "%VENV_DIR%\\Scripts\\python.exe" (
                        python -m venv "%VENV_DIR%"
                    )
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install --upgrade pip
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo 'Training ML model...'

                bat '''
                    "%VENV_DIR%\\Scripts\\python.exe" train_model.py
                '''
            }
        }

        stage('Start API') {
            steps {
                echo 'Starting API...'

                bat '''
                    start "Jenkins API" /B "%VENV_DIR%\\Scripts\\python.exe" app.py
                    timeout /t 10 /nobreak
                '''
            }
        }

        stage('Test API') {
            steps {
                echo 'Testing API...'

                bat '''
                    "%VENV_DIR%\\Scripts\\python.exe" test_prediction.py
                '''
            }
        }
    }

    post {

        success {
            echo '=========================================='
            echo ' Jenkins Pipeline Completed Successfully'
            echo '=========================================='
        }

        failure {
            echo '=========================================='
            echo ' Jenkins Pipeline Failed'
            echo ' Check the Console Output'
            echo '=========================================='
        }

        always {
            echo 'Pipeline execution completed.'
        }
    }
}
```
