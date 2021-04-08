#!/bin/bash
set -euo pipefail

NS_AND_SA="auth,default
auth,dex
cert-manager,cert-manager
cert-manager,cert-manager-cainjector
cert-manager,cert-manager-webhook
cert-manager,default
default,default
istio-operator,default
istio-operator,istio-operator
istio-system,cluster-local-gateway-service-account
istio-system,default
istio-system,istio-ingressgateway-service-account
istio-system,istio-reader-service-account
istio-system,istiod-service-account
istio-system,kiali-service-account
istio-system,prometheus
mlflow,default
mlflow,minio
mlflow,minio-update-prometheus-secret
mlflow,mlflow
mlflow,mysql
knative-serving,controller
knative-serving,default
kube-node-lease,default
kube-public,default
kube-system,attachdetach-controller
kube-system,bootstrap-signer
kube-system,certificate-controller
kube-system,clusterrole-aggregation-controller
kube-system,coredns
kube-system,cronjob-controller
kube-system,daemon-set-controller
kube-system,default
kube-system,deployment-controller
kube-system,disruption-controller
kube-system,endpoint-controller
kube-system,expand-controller
kube-system,generic-garbage-collector
kube-system,horizontal-pod-autoscaler
kube-system,job-controller
kube-system,kube-proxy
kube-system,namespace-controller
kube-system,node-controller
kube-system,persistent-volume-binder
kube-system,pod-garbage-collector
kube-system,pv-protection-controller
kube-system,pvc-protection-controller
kube-system,replicaset-controller
kube-system,replication-controller
kube-system,resourcequota-controller
kube-system,service-account-controller
kube-system,service-controller
kube-system,statefulset-controller
kube-system,storage-provisioner
kube-system,token-cleaner
kube-system,ttl-controller
kubeflow-operator,default
kubeflow-operator,kubeflow-operator
kubeflow,admission-webhook-service-account
kubeflow,application-controller-service-account
kubeflow,argo
kubeflow,argo-ui
kubeflow,centraldashboard
kubeflow,default
kubeflow,jupyter-web-app-service-account
kubeflow,katib-controller
kubeflow,katib-ui
kubeflow,metadata-ui
kubeflow,ml-pipeline
kubeflow,ml-pipeline-persistenceagent
kubeflow,ml-pipeline-scheduledworkflow
kubeflow,ml-pipeline-ui
kubeflow,ml-pipeline-viewer-crd-service-account
kubeflow,notebook-controller-service-account
kubeflow,pipeline-runner
kubeflow,profiles-controller-service-account
kubeflow,pytorch-operator
kubeflow,seldon-manager
kubeflow,spark-operatoroperator-sa
kubeflow,spark-operatorspark
kubeflow,spartakus
kubeflow,tf-job-dashboard
kubeflow,tf-job-operator"

for NS_SA in $NS_AND_SA ; do
        (
            export NS=$(echo $NS_SA |cut -d , -f 1)
            export SA=$(echo $NS_SA |cut -d , -f 2)
            while ! kubectl get sa -n $NS $SA 2>/dev/null; do
                echo "waiting for sa $SA in ns $NS to be created so we can patch regcreds into it..."
                sleep 10
            done
            kubectl patch serviceaccount -n $NS \
                $SA -p '{"imagePullSecrets": [{"name": "regcred"}]}'
        ) &
done
