pipeline {
    agent any

    parameters {
        choice(name: "VERSION", choices: ["1.1.1", "1.2.1", "1.3.1"], description: "Version to choose")
        booleanParam(name: "executeTests", defaultValue: true, description: "Choose to test")
    }
    tools {
        dockerTool 'docker'
    }
    
    environment {
        GIT_REPO = 'https://github.com/BODLAHRUTHIK/hello-world-app.git'
        GIT_CREDENTIALS_ID = 'github-credentials'
        DOCKER_REPO = 'hruthikbodla/myprojects'
        DOCKER_CREDENTIALS_ID = 'dockerhub-creds'
        GIT_BRANCH = 'main'
        REPO_DIR = "${WORKSPACE}"
        AWS_REGION = 'ap-south-1'
        EKS_CLUSTER_NAME = 'eks-cluster'
        HELM_CHART_REPO = 'https://github.com/BODLAHRUTHIK/my-flask-helm.git'
        AWS_ACCOUNT_ID = '874789631010' // Ensure you have this value
        AWS_ROLE_ARN = 'arn:aws:iam::874789631010:role/cluster-access-2'
        AWS_ROLE_SESSION_NAME = 'JenkinsSession'
        PATH = "/var/jenkins_home/bin:$PATH"
        AWS_CREDENTIALS_FILE = "${WORKSPACE}/.aws/credentials"
    }
    

    stages {
        stage('Install AWS CLI') {
            steps {
                script {
                    // Download AWS CLI installation script
                    sh 'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"'
                    sh 'unzip -qo awscliv2.zip'
                    // Install AWS CLI to specified directory
                    sh './aws/install -i /var/jenkins_home/aws-cli -b /var/jenkins_home/bin --update'
                    // Verify AWS CLI installation
                    sh '/var/jenkins_home/aws-cli/v2/current/bin/aws --version'
                }
            }
        }


        


        stage('Download and Install Helm') {
            steps {
                script {
                    
                    sh 'curl -LO https://get.helm.sh/helm-v3.15.2-linux-amd64.tar.gz'
                    sh 'tar -zxvf helm-v3.15.2-linux-amd64.tar.gz'
                    sh 'mv linux-amd64/helm ~/bin/helm'  // Assuming ~/bin is in PATH
                    sh 'helm version'  // Verify installation
                }
            }
        }



        

        stage('Install Tools') {
            steps {
                script {
                    // Install kubectl if not already installed
                    if (!commandExists('kubectl')) {
                        sh '''
                        curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
                        chmod +x kubectl
                        mv kubectl /var/jenkins_home/bin/kubectl
                        '''
                        sh 'kubectl version --client' // Verify installation
                    }

                    // Proceed with other tool installations like Helm
                }
            }
        }

        stage('Git Clone') {
            steps {
                echo 'Cloning the GitHub repository'
                checkout([$class: 'GitSCM',
                          branches: [[name: "*/${env.GIT_BRANCH}"]],
                          doGenerateSubmoduleConfigurations: false,
                          extensions: [],
                          submoduleCfg: [],
                          userRemoteConfigs: [[url: env.GIT_REPO, credentialsId: env.GIT_CREDENTIALS_ID]]
                ])
            }
        }

        stage('Build') {
            steps {
                echo "Building Docker image here"
                script {
                    dir("${REPO_DIR}/hello-world-app/project-flask") {
                        sh "docker build -t ${DOCKER_REPO}:${params.VERSION} ."
                    }

                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh "docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD"
                    }
                    sh "docker push ${DOCKER_REPO}:${params.VERSION}"
                }
            }
        }

        stage('Test') {
            when {
                expression {
                    params.executeTests == true
                }
            }
            steps {
                echo "Running tests"
                echo "Selected version: ${params.VERSION}"
            }
        }

        stage('Clone Helm Chart Repository') {
            steps {
                echo 'Cloning Helm chart repository...'
                script {
                    sh 'rm -rf my-flask-helm' // Clean up any previous clone
                    sh "git clone ${HELM_CHART_REPO}"
                }
            }
        }
        stage('Configure AWS Credentials') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                    sh 'aws configure list'  // Verify AWS CLI configuration
                }
            }
        }

        stage('Fetch Kubeconfig-1') {
            steps {

                sh "aws eks update-kubeconfig --name ${EKS_CLUSTER_NAME} --region ${AWS_REGION}"
                sh 'kubectl config get-contexts'

                sh 'cat /var/jenkins_home/.kube/config'
                sh 'chmod 666 /var/jenkins_home/.kube/config'
                sh 'aws sts get-caller-identity'
                sh "aws eks get-token --cluster-name=${EKS_CLUSTER_NAME} --region ${AWS_REGION}"
                sh '''
                        token=$(aws eks get-token --cluster-name ${EKS_CLUSTER_NAME} --region ${AWS_REGION} --output text --query 'status.token')
                        kubectl get pods --all-namespaces --kubeconfig=/var/jenkins_home/.kube/config
                   '''
                script {
                    dir('my-flask-helm/new-chart') {
                            sh "helm dependency update"
                            sh "helm upgrade --install my-app . --namespace apps --set image.tag=${params.VERSION}"
                        }
                }

            }
        }

    }
}

def commandExists(String command) {
    return sh(script: "command -v $command", returnStatus: true) == 0
}
