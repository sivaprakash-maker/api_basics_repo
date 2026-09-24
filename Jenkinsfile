
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
                checkout scm
            }
        }

        stage('Set Up Python Environment') {
            steps {
                bat '''
                    echo Creating Python virtual environment...

                    if exist "%VENV_DIR%" (
                        echo Removing existing virtual environment...
                        rmdir /s /q "%VENV_DIR%"
                    )

                    python -m venv "%VENV_DIR%"

                    echo Upgrading pip...
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install --upgrade pip

                    echo Installing requirements...
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install -r requirements.txt

                    echo Installing requests...
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install requests
                '''
            }
        }

        stage('Train Model') {
            steps {
                bat '''
                    echo Training model...

                    "%VENV_DIR%\\Scripts\\python.exe" train_model.py
                '''
            }
        }

        stage('Start API & Smoke Test') {
            steps {
                bat '''
                    echo Starting Flask API...

                    start "FlaskAPI" /B cmd /c ""%VENV_DIR%\\Scripts\\python.exe" app.py > app.log 2>&1"

                    echo Waiting for API to become ready...

                    set READY=0

                    for /L %%i in (1,1,30) do (
                        powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/' -UseBasicParsing -TimeoutSec 2; if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }"

                        if not errorlevel 1 (
                            set READY=1
                            echo API is up.
                            goto :API_READY
                        )

                        echo Waiting... %%i/30
                        timeout /t 1 /nobreak >nul
                    )

                    :API_READY

                    if "%READY%"=="0" (
                        echo API did not start in time.
                        echo.
                        echo ===== app.log =====
                        if exist app.log (
                            type app.log
                        )
                        echo ===================
                        exit /b 1
                    )

                    echo Running prediction smoke test...

                    "%VENV_DIR%\\Scripts\\python.exe" test_prediction.py
                '''
            }
        }
    }

    post {

        always {
            bat '''
                echo.
                echo ===== Cleaning up Flask API =====

                powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*app.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

                echo API cleanup completed.
            '''

            archiveArtifacts artifacts: 'house_model.pkl, app.log',
                             allowEmptyArchive: true
        }

        success {
            echo 'Build, train, and smoke test succeeded.'
        }

        failure {
            echo 'Pipeline failed — check app.log and the Jenkins console output for details.'
        }

        cleanup {
            bat '''
                echo Removing Python virtual environment...

                if exist "%VENV_DIR%" (
                    rmdir /s /q "%VENV_DIR%"
                )

                echo Cleanup completed.
            '''
        }
    }
}

