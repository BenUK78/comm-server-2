pipeline {
    agent {
        kubernetes {
            label 'python-buildah-builder'
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    some-label: some-label-value
spec:
  serviceAccountName: jenkins-deployer
  containers:
  - name: python
    image: 'python:3.8-slim'
    command:
      - cat
    tty: true
    resources:
      limits:
        memory: 2Gi
        cpu: 1
  - name: buildah
    image: quay.io/buildah/stable:v1.29
    command:
      - cat
    tty: true
    securityContext:
      privileged: true
    resources:
      limits:
        memory: 2Gi
        cpu: 1
    volumeMounts:
    - name: docker-registry-tls
      mountPath: /etc/ssl/certs/ca-certificates.crt
      subPath: ca.crt
  volumes:
  - name: docker-registry-tls
    secret:
      secretName: docker-registry-tls
                '''
        }
    }
    
    environment {
        GITHUB_BRANCH = 'main'
        KUBE_CREDENTIALS = 'jenkins-kubectl-deployer'
    }
    
    stages {



        // REMEMBER: KUBECTL NEEDS TO BE USING A SA WITH ENOUGH PRIV (JENKINS-DEPLOYER). SET THIS IN MANAGE JENKINS > CLOUDS > KUBERNETES > POD TEMPLATES > JAVA-BUILDAH-AGENT > SERVICE ACCOUNT (SCROLL TO BTM)

        stage('Install Kubectl v1.29.10 & Check') {
            steps {
                container('python') {
                    sh '''

                        # Install Curl
                        apt-get update && apt-get install -y curl 

                        # Install Kubectl v1.29.10
                        curl -LO "https://dl.k8s.io/release/v1.29.10/bin/linux/amd64/kubectl"
                        chmod +x kubectl
                        mv kubectl /usr/local/bin/
                        echo "Kubectl v1.29.10 Installed"
                        
                        echo "=== Detailed Authentication Diagnostics ==="

                        echo "Kubectl Version:"
                        kubectl version --client

                        echo "\n\nChecking kubectl installation:"
                        which kubectl
                            
                        echo "\n\nListing kubeconfig locations:"
                        ls -la ~/.kube || echo "No ~/.kube directory"
                            
                        echo "\n\nEnvironment Variables:"
                        env | grep -E 'KUBE|KUBERNETES'
                            
                        echo "\n\nAttempting to list contexts:"
                        kubectl config get-contexts || echo "Failed to get contexts"
                            
                        echo "\n\nCurrent context:"
                        kubectl config current-context || echo "No current context set"

                        echo "\n1. Current Context Details:"
                        kubectl config view -o jsonpath='{.current-context}'
                        
                        echo "\n\n2. Service Account Details:"
                        kubectl get serviceaccount jenkins-deployer -n jenkins -o yaml
                        
                        echo "\n\n3. Whoami Check:"
                        kubectl auth whoami || echo "Whoami command failed"
                        
                        echo "\n\n4. Detailed Permissions:"
                        kubectl auth can-i --list
                        
                        echo "\n\n5. Cluster Information:"
                        kubectl cluster-info
                        
                        echo "\n\n6. Attempt to Get Nodes (Detailed):"
                        kubectl get nodes -v=8
                    '''
                }
            }
        }

        // stage('Delete Existing Job') {
        //     steps {
        //         container('python') {
        //             script {
        //                 withKubeConfig([credentialsId: 'jenkins-kubectl-deployer']) {
        //                     sh '''
        //                         # Disable command echoing
        //                         set +x

        //                         # Exit immediately if a command exits with a non-zero status
        //                         set -e                                
                                
        //                         # Check if the job exists and delete it if it does
        //                         if kubectl get job comm-server-2-job -n default; then
        //                             echo "Deleting existing job: comm-server-2-job"
        //                             kubectl delete job comm-server-2-job -n default
        //                         else
        //                             echo "Job does not exist: comm-server-2-job in the default ns"
        //                         fi
        //                     '''
        //                 }
        //             }
        //         }
        //     }
        // }

       
        // stage('Install Dependencies') {
        //     steps {
        //         container('python') {
        //             sh 'pip install -r requirements.txt'
        //         }
        //     }
        // }
        
        // stage('Test') {
        //     steps {
        //         container('python') {
        //             sh 'python -m pytest'
        //         }
        //     }
        // }

        stage('Build & Push Image to local Docker Registry') {
            steps {
                container('buildah') {
                    script {
                        sh '''
                            # Configure insecure registry
                            mkdir -p /etc/containers/registries.d
                            echo '{"docker-registry.docker-registry.svc.cluster.local:5000": {"sigstore": ""}}' > /etc/containers/registries.d/insecure.yaml
                            
                            # Build image
                            buildah bud -t docker-registry.docker-registry.svc.cluster.local:5000/comm-server-2:${BUILD_NUMBER} .
                            
                            # Push image
                            # buildah push --tls-verify=false docker-registry.docker-registry.svc.cluster.local:5000/comm-server-2:${BUILD_NUMBER}
                            buildah push docker-registry.docker-registry.svc.cluster.local:5000/comm-server-2:${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }

        stage('Set k8s-deployment.yaml') {
            steps {
                container('python') {
                    script {
                        sh '''
                            # Update image tag in deployment file
                            sed -i "s/IMAGE_TAG/${BUILD_NUMBER}/g" k8s-deployment.yaml
                            
                            # Display updated deployment file
                            cat k8s-deployment.yaml
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('python') {
                    script {
                        withKubeConfig([credentialsId: 'jenkins-kubectl-deployer']) {
                            sh 'kubectl apply -f k8s-deployment.yaml -n app-test'
                        }
                    }
                }
            }
        }

        // stage('Verify Job') {
        //     steps {
        //         container('python') {
        //             script {
        //                 withKubeConfig([credentialsId: 'jenkins-kubectl-deployer']) {
        //                     sh '''
        //                         # Check job status
        //                         kubectl get job -n default comm-server-2-job
                                
        //                         # Wait for job completion
        //                         while true; do
        //                             job_status=$(kubectl get job -n default comm-server-2-job -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}')
        //                             if [ "$job_status" = "True" ]; then
        //                                 echo "Job completed successfully"
        //                                 break
        //                             fi
        //                             echo "Waiting for job to complete..."
        //                             sleep 5
        //                         done
                                
        //                         # Get detailed job information
        //                         kubectl describe job -n default comm-server-2-job
        //                     '''
        //                 }
        //             }
        //         }
        //     }
        // }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}