name = "thumbnail"
server = "https://api.provo1.endurancemb.com:6443"

init = [:]
fin = [:]
branch_type = ''

if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
    init = [ ns: "${name}-beta", name: "staging" ]
    fin = [ ns: "${name}-prod", name: "prod" ]
    branch_type = 'main'
}
else if (env.BRANCH_NAME == 'beta') {
    init = [ ns: "${name}-beta", name: "beta" ]

    // needed for credential name
    fin = [ ns: "${name}-beta", name: "beta" ]
    branch_type = 'beta'
}
else {
    // all other branches
    init = [ ns: "${name}-alpha", name: env.BRANCH_NAME.replace('/', '-').replace('_','-').toLowerCase() ]
    
    // needed for credential name
    fin = [ ns: "${name}-beta", name: "beta" ]
    branch_type = 'feature'
}

def kubectl(namespace, cmd) {
    token_name = "\$token_${namespace.replace('-', '_')}"
    sh "kubectl --token $token_name --server $server -n $namespace $cmd"
}

def oc(namespace, cmd) {
    token_name = "\$token_${namespace.replace('-', '_')}"
    sh "oc --token $token_name --server $server -n $namespace $cmd"
}

node {
    withCredentials([
        string(credentialsId:"${init.ns}-okdtoken", variable: "token_${init.ns.replace('-', '_')}"), 
        string(credentialsId:"${fin.ns}-okdtoken", variable: "token_${fin.ns.replace('-', '_')}"), 
    ])
    {
        stage('Build') {
            
            if (branch_type == 'feature') {
                checkout scm
                sh """
                oc --token \$token_${init.ns.replace('-', '_')} --server $server --namespace ${init.ns} get deployment ${init.name} || \${NF_BIN_PATH}helm install --timeout '20m' --kube-apiserver $server --kube-token \$token_${init.ns.replace('-', '_')} --wait --namespace ${init.ns} -f helm/base.yaml -f helm/branch.yaml --set branch=${env.BRANCH_NAME} ${init.name} helm/chart
                """
            }

            if (branch_type == 'main') {
                oc(fin.ns, "start-build ${fin.name}")
            }

            oc(init.ns, "start-build --wait --follow ${init.name}")
        }
        stage('Stage') {
            kubectl(init.ns, "get pods -l'app.kubernetes.io/name=${init.name}'") 

            kubectl(init.ns, "rollout restart deployment/${init.name}")
            kubectl(init.ns, "rollout status deployment/${init.name}")

            kubectl(init.ns, "get pods -l'app.kubernetes.io/name=${init.name}'") 
        }
        stage('Test') {
            token_name = "\$token_${init.ns.replace('-', '_')}"

            sh """
                pod=\$(oc --token $token_name --server $server --namespace ${init.ns} get pods -l'app.kubernetes.io/name=${init.name}' --sort-by ".metadata.creationTimestamp" | awk '{ print \$1 }' | tail -n1)
                echo "Found pod for testing: \$pod"

                kubectl --token $token_name --server $server --namespace ${init.ns} exec pod/\$pod -- sh -c 'echo \"Running tests on \$HOSTNAME / \$OPENSHIFT_BUILD_NAME\";  pytest -o junit_logging=all --junit-xml /tmp/result; touch /tmp/done; echo DONE_TESTING'


                result=\$(for i in \$(seq 1000);
                    do
                    done=\$(kubectl --token $token_name --server $server exec --namespace ${init.ns} pod/\$pod -- sh -c "(test -f /tmp/done && echo 1) || true") || true; 
                    if [[ "\$done" == "1" ]]; 
                        then kubectl --token $token_name --server $server exec --namespace ${init.ns} pod/\$pod -- cat /tmp/result; break; 
                        else sleep 10; test \$k_verbose == "1" && echo "waiting for pod: \$result";  
                    fi;
                    done)

                echo "DONE!"
                echo \$result > test_results.xml
                
                """

            junit 'test_results.xml'
            sh "test ${currentBuild.currentResult} != UNSTABLE"

        }
        stage('Deploy') {
            if (branch_type == 'main') {
                //oc(fin.ns, "start-build --wait --follow ${fin.name}")
                oc(fin.ns, "logs -f bc/${fin.name}")
                oc(fin.ns, "tag ${fin.name}:test ${fin.name}:latest")
                kubectl(fin.ns, "rollout restart deployment/${fin.name}")
                kubectl(fin.ns, "rollout status deployment/${fin.name}")
            }
            else {
                sh "echo Not on Main branch, skipping final deploy stage"
            }
        }
    }
}
