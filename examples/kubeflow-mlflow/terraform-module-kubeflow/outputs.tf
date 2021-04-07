output "wait_for_kubeflow" {
  value = []
  depends_on = [null_resource.wait_for_certs]
}
