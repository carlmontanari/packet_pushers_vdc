pipeline {
    agent {
        docker {
            image 'my_network_as_code'
            args '--user root'
        }
    }
    stages {
        stage('Checkout and Prepare') {
            steps {
                checkout scm
            }
        }
        stage('Run Syntax Checks') {
            steps {
                sh 'ansible-playbook generate_configurations.yaml --syntax-check'
                sh 'ansible-playbook backup_configurations.yaml --syntax-check'
                sh 'ansible-playbook deploy_configurations.yaml --syntax-check'
                sh 'ansible-playbook validate_configurations.yaml --syntax-check'
                sh 'ansible-playbook rollback_configurations.yaml --syntax-check'
            }
        }
        stage('Validate User Inputs') {
            steps {
                script {
                    result = sh(script: 'python3 validate_user_input.py', returnStatus: true)
                    if (result > 0) {
                        currentBuild.result = 'ABORTED'
                        error('Integration testing FAILED')
                    }
                }
            }
        }
        stage ('Render Configurations') {
            steps {
                sh 'ansible-playbook generate_configurations.yaml'
            }
        }
        stage ('Backup Configurations') {
            steps {
                sh 'ansible-playbook backup_configurations.yaml'
            }
        }
        stage ('Deploy') {
            steps {
                sh 'ansible-playbook deploy_configurations.yaml'
            }
        }
        stage ('Validate') {
            steps {
                sh 'sleep 30'
                script {
                    result = sh(script: 'ansible-playbook validate_configurations.yaml', returnStatus: true)
                    if (result > 0) {
                        sh 'ansible-playbook rollback_configurations.yaml'
                        currentBuild.result = 'ABORTED'
                        error('Functional testing FAILED')
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
