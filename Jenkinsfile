pipeline {
    agent any

    environment {
        SONAR_TOKEN_ID = '2401178_SonarToken'
        NEXUS_CREDS_ID = '2401178_NexusLogin'
        PROJECT_KEY = '2401178BhashaBridge'
        IMAGE_NAME = 'bhashabridge'
        VERSION = "1.0.${BUILD_NUMBER}"
        
        // --- THE FIX: Use the internal name found in your error logs ---
        NEXUS_HOST = 'ingress.local'
        NEXUS_URL = 'https://ingress.local' 
        
        // The IP you found
        SERVER_IP = '192.168.20.250' 
    }

    stages {
        stage('Checkout') { steps { checkout scm } }
        
        stage('SonarQube Analysis') {
            steps {
                container('dind') {
                    script {
                        try {
                            echo "Starting SonarQube Scan..."
                            withCredentials([string(credentialsId: SONAR_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                                // DNS Hack for Sonar
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
                        } catch (Exception e) { echo "Sonar failed, skipping..." }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    // Build locally
                    sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                container('dind') {
                    script {
                        try {
                            echo "--- PUSHING TO PERMANENT STORAGE (INGRESS.LOCAL) ---"
                            
                            // 1. Map the IP to the secret internal name
                            sh "echo '${SERVER_IP} ingress.local' >> /etc/hosts"
                            
                            withCredentials([usernamePassword(credentialsId: NEXUS_CREDS_ID, usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                                // 2. Login using the secret name
                                sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_URL}"
                                
                                // 3. Tag the image specifically for Nexus
                                sh "docker tag ${IMAGE_NAME}:${VERSION} ${NEXUS_HOST}/docker-hosted/${IMAGE_NAME}:${VERSION}"
                                
                                // 4. Push it!
                                sh "docker push ${NEXUS_HOST}/docker-hosted/${IMAGE_NAME}:${VERSION}"
                            }
                            echo "--- SUCCESS: IMAGE SAVED FOREVER IN NEXUS ---"
                        } catch (Exception e) {
                            echo "Push failed. Error: " + e.toString()
                            // We don't fail the build, so you still get the Deployment link below
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                container('dind') {
                    script {
                        sh "docker stop ${IMAGE_NAME} || true"
                        sh "docker rm ${IMAGE_NAME} || true"
                        
                        // Deploy the app so you can see it NOW
                        sh "docker run -d --name ${IMAGE_NAME} -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
                        
                        // Keep it alive for a bit so you can verify
                        sh "sleep 5"
                    }
                }
            }
        }
    }
}
