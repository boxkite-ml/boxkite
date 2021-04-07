/*resource "k8s_manifest" "mlflow_poddefault" {
  depends_on = [module.kubeflow.wait_for_kubeflow, kubernetes_namespace.admin]
  timeouts {
    delete = "15m"
  }
  content = templatefile("${path.module}/poddefault.yaml", {})
}

resource "kubernetes_namespace" "admin" {
  metadata {
    name = "admin"
  }
}*/

// TODO: try and extract the profile CRD from kubeflow and pre-create it in
// terraform so that the setup wizard doesn't fail with the namespace already
// existing.
