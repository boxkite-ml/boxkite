resource "time_sleep" "wait_for_namespace" {
  create_duration = "10s"
  depends_on = [k8s_manifest.admin_profile]
}

resource "k8s_manifest" "mlflow_poddefault" {
  depends_on = [time_sleep.wait_for_namespace]
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
