pipeline {
    agent any

    environment {
        // These match the IDs we created in Jenkins
        SONAR_TOKEN_ID = '2401178_SonarToken'
        NEXUS_CREDS_ID = '2401178_NexusLogin'
        
        // Your specific details
        PROJECT_KEY = '2401178BhashaBridge'
        IMAGE_NAME = 'bhashabridge'
        VERSION = "1.0.${BUILD_NUMBER}"
        NEXUS_URL = 'nexus.imcc.com'
        NEXUS_REPO = 'docker-hosted' // Assuming this is the repo name
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner' // Asking Jenkins for the tool
                    withSonarQubeEnv('SonarQube') { // Matches the system config name
                        sh "${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=${PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://sonarqube.imcc.com \
                        -Dsonar.login=$SONAR_TOKEN" 
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: NEXUS_CREDS_ID, usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                        // Login to Nexus Docker Registry
                        sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_URL}"
                        
                        // Tag image for Nexus
                        sh "docker tag ${IMAGE_NAME}:${VERSION} ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${VERSION}"
                        
                        // Push image
                        sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${VERSION}"
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Stop old container if running (ignore error if not running)
                    sh "docker stop ${IMAGE_NAME} || true"
                    sh "docker rm ${IMAGE_NAME} || true"
                    
                    // Run new container
                    sh "docker run -d --name ${IMAGE_NAME} -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
                }
            }
        }
    }
}
