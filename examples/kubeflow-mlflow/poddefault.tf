resource "k8s_manifest" "mlflow_poddefault" {
  depends_on = [kubernetes_deployment.kubeflow_operator, k8s_manifest.kubeflow_application_crd]
  timeouts {
    delete = "15m"
  }
  content = templatefile("${path.module}/poddefaults.yaml", {})
}
