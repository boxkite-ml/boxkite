
resource "kubernetes_namespace" "kubeflow_operator" {
  metadata {
    name = var.kubeflow_operator_namespace
  }
}

resource "k8s_manifest" "kubeflow_operator_crd" {
  content = templatefile("${path.module}/manifests/kubeflow/operator-crd.yaml", {})
}

resource "kubernetes_service_account" "kubeflow_operator" {
  metadata {
    name      = "kubeflow-operator"
    namespace = kubernetes_namespace.kubeflow_operator.metadata.0.name
  }
}

resource "kubernetes_cluster_role" "kubeflow_operator" {
  metadata {
    name = "kubeflow-operator"
    labels = {
      "kubernetes.io/bootstrapping" = "rbac-defaults"
    }

    annotations = {
      "rbac.authorization.kubernetes.io/autoupdate" = "true"
    }
  }

  rule {
    verbs      = ["*"]
    api_groups = ["*"]
    resources  = ["*"]
  }

  rule {
    verbs             = ["*"]
    non_resource_urls = ["*"]
  }
}

resource "kubernetes_cluster_role_binding" "kubeflow_operator" {
  metadata {
    name = "kubeflow-operator"
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.kubeflow_operator.metadata.0.name
    namespace = kubernetes_namespace.kubeflow_operator.metadata.0.name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
}

resource "kubernetes_deployment" "kubeflow_operator" {
  depends_on = [k8s_manifest.kubeflow_operator_crd, kubernetes_cluster_role_binding.kubeflow_operator]
  metadata {
    name      = "kubeflow-operator"
    namespace = kubernetes_namespace.kubeflow_operator.metadata.0.name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        name = "kubeflow-operator"
      }
    }

    template {
      metadata {
        labels = {
          name = "kubeflow-operator"
        }
      }

      spec {
        automount_service_account_token = true
        container {
          name    = "kubeflow-operator"
          image   = "aipipeline/kubeflow-operator:v${var.kubeflow_operator_version}"
          command = ["kfctl"]

          env {
            name = "WATCH_NAMESPACE"

            value_from {
              field_ref {
                field_path = "metadata.namespace"
              }
            }
          }

          env {
            name = "POD_NAME"

            value_from {
              field_ref {
                field_path = "metadata.name"
              }
            }
          }

          env {
            name = "OPERATOR_NAME"

            value_from {
              field_ref {
                field_path = "metadata.name"
              }
            }
          }

          image_pull_policy = "Always"
        }

        service_account_name = kubernetes_service_account.kubeflow_operator.metadata.0.name
      }
    }
  }
}