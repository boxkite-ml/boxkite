output "wait_for_kubeflow" {
  value = []
  depends_on = [k8s_manifest.kubeflow_kfdef, k8s_manifest.kubeflow_application_crd]
}
