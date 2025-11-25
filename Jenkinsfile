pipeline {
    agent any

    environment {
        // IDs from Jenkins
        SONAR_TOKEN_ID = '2401178_SonarToken'
        NEXUS_CREDS_ID = '2401178_NexusLogin'
        
        // Project Details
        PROJECT_KEY = '2401178BhashaBridge'
        IMAGE_NAME = 'bhashabridge'
        VERSION = "1.0.${BUILD_NUMBER}"
        
        // Nexus Details
        NEXUS_URL = 'nexus.imcc.com'
        NEXUS_REPO = 'docker-hosted'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout must happen in the default agent
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                // SWITCH TO THE BIG CONTAINER (4GB RAM + Docker)
                container('dind') {
                    script {
                        withCredentials([string(credentialsId: SONAR_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                            // We manually run the scanner using Docker 
                            // This bypasses the memory limit of the small agent entirely
                            sh """
                            docker run --rm \
                                -e SONAR_HOST_URL=http://sonarqube.imcc.com \
                                -e SONAR_TOKEN=${SONAR_TOKEN} \
                                -v \$(pwd):/usr/src \
                                sonarsource/sonar-scanner-cli \
                                -Dsonar.projectKey=${PROJECT_KEY} \
                                -Dsonar.sources=. \
                                -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/.git/**
                            """
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                // SWITCH TO THE BIG CONTAINER
                container('dind') {
                    script {
                        sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                    }
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                // SWITCH TO THE BIG CONTAINER
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
                // SWITCH TO THE BIG CONTAINER
                container('dind') {
                    script {
                        // Stop old container if running
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
