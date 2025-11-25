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
        
        // --- MEMORY FIX: REDUCED TO 128MB ---
        SONAR_SCANNER_OPTS = "-Xmx128m"
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
                    def scannerHome = tool 'SonarScanner' 
                    withSonarQubeEnv('sonar-imcc-2401060') { 
                        withCredentials([string(credentialsId: SONAR_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                            // Added exclusions to save memory by ignoring useless files
                            sh "${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/venv/**,**/__pycache__/**,**/.git/**,**/*.html \
                            -Dsonar.host.url=http://sonarqube.imcc.com \
                            -Dsonar.token=${SONAR_TOKEN}" 
                        }
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
                        sh "docker login -u ${NEXUS_USER} -p ${NEXUS_PASS} ${NEXUS_URL}"
                        sh "docker tag ${IMAGE_NAME}:${VERSION} ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${VERSION}"
                        sh "docker push ${NEXUS_URL}/${NEXUS_REPO}/${IMAGE_NAME}:${VERSION}"
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
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
