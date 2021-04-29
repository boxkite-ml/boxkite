#!/bin/bash
set -xe
helm delete prometheus-grafana || true
helm install prometheus-grafana .
sleep 10
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=prometheus-grafana" -o jsonpath="{.items[0].metadata.name}")
# le unfriendly hack
pkill -f 'kubectl.*port-forward' || true
kubectl --namespace default port-forward $POD_NAME 3001:3000 &
kubectl exec -ti $POD_NAME --container grafana -- bash
