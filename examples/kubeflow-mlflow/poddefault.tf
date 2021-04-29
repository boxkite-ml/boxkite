resource "null_resource" "wait_kubeflow_crds" {
  depends_on = [module.kubeflow.wait_for_kubeflow]

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = "while [[ ! \"$(kubectl get crds | grep 'kubeflow.org' | wc -l)\" -eq \"12\" ]]; do echo \"Waiting for Kubeflow CRDs\"; kubectl get crds | grep 'kubeflow.org' | wc -l; sleep 5; done"
  }
}

resource "time_sleep" "wait_kubeflow_crds" {
  create_duration = "30s"
  depends_on = [null_resource.wait_kubeflow_crds]
}

resource "k8s_manifest" "admin_profile" {
  depends_on = [time_sleep.wait_kubeflow_crds]
  timeouts {
    delete = "15m"
  }
  content = templatefile("${path.module}/profile.yaml", {})
}

resource "null_resource" "wait_namespace" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = "while [[ ! \"$(kubectl get ns | grep 'admin' | wc -l)\" -eq \"1\" ]]; do echo \"Waiting for admin namespace\"; sleep 5; done"
  }
  depends_on = [module.kubeflow.wait_for_kubeflow, k8s_manifest.admin_profile]
}

resource "k8s_manifest" "mlflow_poddefault" {
  depends_on = [null_resource.wait_namespace]
  timeouts {
    delete = "15m"
  }
  content = templatefile("${path.module}/poddefault.yaml", {})
}

resource "kubernetes_cluster_role_binding" "notebook_access_k8s" {
  metadata {
    name = "notebook-access-k8s"
  }
  subject {
    kind      = "ServiceAccount"
    name      = "default"
    namespace = "admin"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
  depends_on = [null_resource.wait_namespace]
}
