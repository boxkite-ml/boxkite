/*

apiVersion: "kubeflow.org/v1alpha1"
kind: PodDefault
metadata:
  name: add-gcp-secret
  namespace: kubeflow
spec:
 selector:
  matchLabels:
    add-gcp-secret: "true"
 desc: "add gcp credential"
 volumeMounts:
 - name: secret-volume
   mountPath: /secret/gcp
 volumes:
 - name: secret-volume
   secret:
    secretName: gcp-secret

*/
