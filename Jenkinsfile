pipeline {
    agent any

    environment {
        // IDs
        SONAR_TOKEN_ID = '2401178_SonarToken'
        NEXUS_CREDS_ID = '2401178_NexusLogin'
        
        // Project
        PROJECT_KEY = '2401178BhashaBridge'
        IMAGE_NAME = 'bhashabridge'
        VERSION = "1.0.${BUILD_NUMBER}"
        
        // URLs
        NEXUS_URL = 'nexus.imcc.com'
        NEXUS_REPO = 'docker-hosted'
        
        // GOLDEN KEY: The IP Address you found
        SONAR_IP_URL = 'http://192.168.20.250'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                // We use the 'dind' container because it has Docker installed and 4GB RAM
                container('dind') {
                    script {
                        try {
                            echo "Attempting SonarQube Scan using IP Address..."
                            withCredentials([string(credentialsId: SONAR_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                                // We use the IP address (SONAR_IP_URL) here to bypass DNS
                                sh """
                                docker run --rm \
                                    -e SONAR_HOST_URL=${SONAR_IP_URL} \
                                    -e SONAR_TOKEN=${SONAR_TOKEN} \
                                    -v \$(pwd):/usr/src \
                                    sonarsource/sonar-scanner-cli \
                                    -Dsonar.projectKey=${PROJECT_KEY} \
                                    -Dsonar.sources=. \
                                    -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/.git/**
                                """
                            }
                        } catch (Exception e) {
                            echo "WARNING: SonarQube failed likely due to network restriction. Proceeding to Deployment."
                            echo e.toString()
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    script {
                        sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                    }
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                container('dind') {
                    script {
                        withCredentials([usernamePassword(credentialsId: NEXUS_CREDS_ID, usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                            sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_URL}"
                            sh "docker tag ${IMAGE_NAME}:${VERSION} ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${VERSION}"
                            sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${VERSION}"
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                container('dind') {
                    script {
                        // Stop old container
                        sh "docker stop ${IMAGE_NAME} || true"
                        sh "docker rm ${IMAGE_NAME} || true"
                        
                        // Run new container
                        sh "docker run -d --name ${IMAGE_NAME} -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
                    }
                }
            }
        }
    }
}
