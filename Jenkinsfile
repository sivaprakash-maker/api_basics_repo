```groovy
pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        API_PORT = '5000'
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

        stage('Python Environment') {
            steps {
                echo 'Creating Python virtual environment...'

                bat '''
                    python --version
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat

                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                    python -m pip install requests
                '''
            }
        }

        stage('Train Model') {
            steps {
                echo 'Training ML model...'

                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat

                    python train_model.py

                    if not exist house_model.pkl (
                        echo ERROR: house_model.pkl was not created.
                        exit /b 1
                    )

                    echo Model training completed successfully.
                    dir house_model.pkl
                '''
            }
        }

        stage('Start API & Smoke Test') {
            steps {
                echo 'Starting API...'

                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat

                    echo Starting Flask API...

                    start "" /B cmd /C "python app.py > app.log 2>&1"

                    echo Waiting for API to become ready...

                    set READY=0

                    for /L %%i in (1,1,30) do (
                        powershell -NoProfile -Command "try { Invoke-WebRequest -Uri http://127.0.0.1:%API_PORT%/ -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"

                        if not errorlevel 1 (
                            set READY=1
                            echo API is UP.
                            goto API_READY
                        )

                        echo API not ready yet... attempt %%i/30
                        timeout /t 1 /nobreak >nul
                    )

                    :API_READY

                    if "%READY%"=="0" (
                        echo ERROR: API did not start within 30 seconds.
                        echo.
                        echo ================= APP LOG =================
                        if exist app.log type app.log
                        echo ============================================
                        exit /b 1
                    )

                    echo.
                    echo API started successfully.
                    echo Running prediction smoke test...
                    echo.

                    python test_prediction.py

                    if errorlevel 1 (
                        echo ERROR: Prediction smoke test failed.
                        exit /b 1
                    )

                    echo.
                    echo Prediction smoke test completed successfully.
                '''
            }
        }
    }

    post {

        always {
            echo 'Saving application log and cleaning API process...'

            bat '''
                echo Checking API process on port %API_PORT%...

                powershell -NoProfile -Command "$p = Get-NetTCPConnection -LocalPort %API_PORT% -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; if ($p) { Write-Host 'Stopping API process:' $p; Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } else { Write-Host 'No API process found on port %API_PORT%.' }"

                echo.
                echo ================= APP LOG =================

                if exist app.log (
                    type app.log
                ) else (
                    echo app.log was not created.
                )

                echo ============================================
            '''

            archiveArtifacts artifacts: 'house_model.pkl, app.log', allowEmptyArchive: true
        }

        success {
            echo '=============================================='
            echo 'BUILD SUCCESS'
            echo 'Model training completed.'
            echo 'API smoke test completed.'
            echo '=============================================='
        }

        failure {
            echo '=============================================='
            echo 'BUILD FAILED'
            echo 'Please check the console output and app.log.'
            echo '=============================================='
        }

        cleanup {
            echo 'Removing Python virtual environment...'

            bat '''
                if exist "%VENV_DIR%" (
                    rmdir /S /Q "%VENV_DIR%"
                    echo Virtual environment removed.
                ) else (
                    echo Virtual environment does not exist.
                )
            '''
        }
    }
}
```
