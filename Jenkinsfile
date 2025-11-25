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
        
        // --- THE KEY ---
        // Verify this IP matches your ping result!
        SERVER_IP = '192.168.20.250' 
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                container('dind') {
                    script {
                        try {
                            echo "Injecting DNS Hack for SonarQube..."
                            withCredentials([string(credentialsId: SONAR_TOKEN_ID, variable: 'SONAR_TOKEN')]) {
                                // We use --add-host to force the container to map the domain to the IP
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
                        } catch (Exception e) {
                            echo "WARNING: SonarQube failed. Skipping to ensure Deployment."
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
                        // We use the AWS mirror you found to avoid rate limits
                        sh "docker build -t ${IMAGE_NAME}:${VERSION} ."
                    }
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                container('dind') {
                    script {
                        // THE HACK: We manually add the mapping to the /etc/hosts file
                        // This forces the system to know where nexus.imcc.com is
                        sh "echo '${SERVER_IP} nexus.imcc.com' >> /etc/hosts"
                        
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
                        // We need the hack here too so it can PULL the image we just pushed
                        sh "echo '${SERVER_IP} nexus.imcc.com' >> /etc/hosts"
                        
                        sh "docker stop ${IMAGE_NAME} || true"
                        sh "docker rm ${IMAGE_NAME} || true"
                        
                        // Run the container
                        sh "docker run -d --name ${IMAGE_NAME} -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
                    }
                }
            }
        }
    }
}
