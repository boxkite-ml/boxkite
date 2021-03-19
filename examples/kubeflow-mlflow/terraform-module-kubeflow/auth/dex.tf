locals {
  dex_crd_manifests = split("\n---\n", templatefile(
    "${path.module}/manifests/dex-crd.yaml",
    {
      namespace   = kubernetes_namespace.auth.metadata.0.name,
      domain_name = var.domain_name
    }
    )
  )
}

resource "k8s_manifest" "dex_crd" {
  count      = length(local.dex_crd_manifests)
  content    = local.dex_crd_manifests[count.index]
}

resource "kubernetes_service_account" "dex" {
  metadata {
    name      = "dex"
    namespace = kubernetes_namespace.auth.metadata.0.name
  }
}

resource "kubernetes_cluster_role" "dex" {
  metadata {
    name = "dex"
  }

  rule {
    verbs      = ["*"]
    api_groups = ["dex.coreos.com"]
    resources  = ["*"]
  }

  rule {
    verbs      = ["create"]
    api_groups = ["apiextensions.k8s.io"]
    resources  = ["customresourcedefinitions"]
  }
}

resource "kubernetes_cluster_role_binding" "dex" {
  metadata {
    name = "dex"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "dex"
    namespace = kubernetes_namespace.auth.metadata.0.name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "dex"
  }
}

resource "kubernetes_secret" "dex" {
  metadata {
    name      = "dex"
    namespace = kubernetes_namespace.auth.metadata.0.name
  }

  data = {
    "config.yaml" = templatefile("${path.module}/configs/dex.yaml", {
      application_secret   = var.application_secret
      client_id            = var.client_id
      issuer               = var.issuer
      namespace            = kubernetes_namespace.auth.metadata.0.name
      oidc_redirect_uri   = var.oidc_redirect_url
      static_email         = var.static_email
      static_password_hash = var.static_password_hash
      static_user_id       = var.static_user_id
      static_username      = var.static_username
      domain_name          = var.domain_name
    })
  }
}

resource "kubernetes_service" "dex" {
  metadata {
    name      = "dex"
    namespace = kubernetes_namespace.auth.metadata.0.name
  }

  spec {
    port {
      name        = "dex"
      protocol    = "TCP"
      port        = 5556
      target_port = "5556"
      node_port   = 32000
    }

    selector = {
      app = "dex"
    }

    type = "NodePort"
  }
}

resource "kubernetes_deployment" "dex" {
  depends_on = [k8s_manifest.dex_crd]
  metadata {
    name      = "dex"
    namespace = kubernetes_namespace.auth.metadata.0.name

    labels = {
      app = "dex"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "dex"
      }
    }

    template {
      metadata {
        labels = {
          app = "dex"
        }
      }

      spec {
        automount_service_account_token = true
        volume {
          name = "config"

          secret {
            secret_name = "dex"

            items {
              key  = "config.yaml"
              path = "config.yaml"
            }
          }
        }

        container {
          name    = "dex"
          image   = "gcr.io/arrikto/dexidp/dex:4bede5eb80822fc3a7fc9edca0ed2605cd339d17"
          command = ["dex", "serve", "/etc/dex/cfg/config.yaml"]

          port {
            name           = "http"
            container_port = 5556
          }

          volume_mount {
            name       = "config"
            mount_path = "/etc/dex/cfg"
          }
        }

        service_account_name = "dex"
      }
    }
  }
}

