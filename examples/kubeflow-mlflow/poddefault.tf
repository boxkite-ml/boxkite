resource "k8s_manifest" "mlflow_poddefault" {
  depends_on = [k8s_manifest.admin_profile]
  timeouts {
    delete = "15m"
  }
  content = templatefile("${path.module}/poddefault.yaml", {})
}

resource "k8s_manifest" "admin_profile" {
  depends_on = [module.kubeflow.wait_for_kubeflow]
  timeouts {
    delete = "15m"
  }
  content = templatefile("${path.module}/profile.yaml", {})
}
