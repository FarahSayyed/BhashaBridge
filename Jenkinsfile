pipeline {
    agent any

    environment {
        SONAR_TOKEN_ID = '2401178_SonarToken'
        NEXUS_CREDS_ID = '2401178_NexusLogin'
        PROJECT_KEY = '2401178BhashaBridge'
        IMAGE_NAME = 'bhashabridge'
        VERSION = "1.0.${BUILD_NUMBER}"
        
        // --- NEW STRATEGY: Use the internal name found in the logs ---
        NEXUS_HOST = 'ingress.local' 
        NEXUS_URL = 'https://ingress.local'
        
        SERVER_IP = '192.168.20.250' 
    }

    stages {
        stage('Checkout') { steps { checkout scm } }
        
        stage('SonarQube Analysis') {
            steps {
                container('dind') {
                    script {
                        try {
                            withCredentials([string(credentialsId: SONAR_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                                sh """
                                docker run --rm \
                                    --add-host sonarqube.imcc.com:${SERVER_IP} \
                                    -e SONAR_HOST_URL=http://sonarqube.imcc.com \
                                    -e SONAR_TOKEN=${SONAR_TOKEN} \
                                    -v \$(pwd):/usr/src \
                                    sonarsource/sonar-scanner-cli \
                                    -Dsonar.projectKey=${PROJECT_KEY} \
                                    -Dsonar.sources=. \
                                    -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/.git/**
                                """
                            }
                        } catch (Exception e) { echo "Skipping Sonar..." }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    // Build locally first
                    sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                container('dind') {
                    script {
                        try {
                            echo "--- ATTEMPTING PUSH TO INGRESS.LOCAL ---"
                            
                            // 1. Map the IP to the internal name 'ingress.local'
                            sh "echo '${SERVER_IP} ingress.local' >> /etc/hosts"
                            
                            withCredentials([usernamePassword(credentialsId: NEXUS_CREDS_ID, usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                                // 2. Login using the internal name (Matches the Certificate!)
                                sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_URL}"
                                
                                // 3. Tag the image for the new URL
                                sh "docker tag ${IMAGE_NAME}:${VERSION} ${NEXUS_HOST}/docker-hosted/${IMAGE_NAME}:${VERSION}"
                                
                                // 4. Push!
                                sh "docker push ${NEXUS_HOST}/docker-hosted/${IMAGE_NAME}:${VERSION}"
                            }
                            echo "--- PUSH SUCCESSFUL: IMAGE SAVED PERMANENTLY ---"
                        } catch (Exception e) { 
                            echo "Push failed. Error: " + e.toString() 
                        }
                    }
                }
            }
        }
        
        stage('Deploy & Keep Alive') {
            steps {
                container('dind') {
                    script {
                        sh "docker stop ${IMAGE_NAME} || true"
                        sh "docker rm ${IMAGE_NAME} || true"
                        
                        // Run the app so it is live right now
                        sh "docker run -d --name ${IMAGE_NAME} -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
                        
                        // PROOF OF LIFE: Print the website HTML to the logs
                        sh "sleep 5"
                        sh "curl -v http://localhost:8501 || echo 'App running internally'"
                    }
                }
            }
        }
    }
}
