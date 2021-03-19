package test

import (
	"strings"
	"testing"
	"time"

	"github.com/gruntwork-io/terratest/modules/helm"
	"github.com/gruntwork-io/terratest/modules/k8s"
	"github.com/gruntwork-io/terratest/modules/logger"
	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	test_structure "github.com/gruntwork-io/terratest/modules/test-structure"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func getDefaultTerraformOptions(t *testing.T) (string, *terraform.Options, error) {

	tempTestFolder := test_structure.CopyTerraformFolderToTemp(t, "..", ".")

	random_id := strings.ToLower(random.UniqueId())

	terraformOptions := &terraform.Options{
		TerraformDir:       tempTestFolder,
		Vars:               map[string]interface{}{},
		MaxRetries:         5,
		TimeBetweenRetries: 5 * time.Minute,
		NoColor:            false,
		Logger:             logger.TestingT,
	}

	return random_id, terraformOptions, nil
}

func getIstioTerraformOptions(t *testing.T) (*terraform.Options, error) {

	tempTestFolder := test_structure.CopyTerraformFolderToTemp(t, "..", "istio")

	terraformOptions := &terraform.Options{
		TerraformDir:       tempTestFolder,
		Vars:               map[string]interface{}{},
		MaxRetries:         5,
		TimeBetweenRetries: 5 * time.Minute,
		NoColor:            false,
		Logger:             logger.TestingT,
	}

	return terraformOptions, nil
}

func TestApplyAndDestroyWithOldValues(t *testing.T) {
	_, options, err := getDefaultTerraformOptions(t)
	assert.NoError(t, err)

	options.Vars["cert_manager_namespace"] = "cert-manager"
	options.Vars["istio_operator_namespace"] = "istio-operator"
	options.Vars["istio_namespace"] = "istio-system"
	options.Vars["ingress_gateway_ip"] = "10.20.30.40"
	options.Vars["use_cert_manager"] = true
	options.Vars["install_istio"] = true
	options.Vars["install_cert_manager"] = true
	options.Vars["domain_name"] = "foo.local"
	options.Vars["letsencrypt_email"] = "foo@bar.local"
	options.Vars["ingress_gateway_annotations"] = map[string]interface{}{"foo": "bar"}
	options.Vars["kubeflow_version"] = "1.0.2"
	options.Vars["kubeflow_operator_version"] = "1.0.0"

	defer terraform.Destroy(t, options)
	_, err = terraform.InitAndApplyE(t, options)
	assert.NoError(t, err)
}

func TestApplyAndDestroyWithSaneValues(t *testing.T) {
	_, options, err := getDefaultTerraformOptions(t)
	assert.NoError(t, err)

	options.Vars["cert_manager_namespace"] = "cert-manager"
	options.Vars["istio_operator_namespace"] = "istio-operator"
	options.Vars["istio_namespace"] = "istio-system"
	options.Vars["ingress_gateway_ip"] = "10.20.30.40"
	options.Vars["use_cert_manager"] = true
	options.Vars["install_istio"] = true
	options.Vars["install_cert_manager"] = true
	options.Vars["domain_name"] = "foo.local"
	options.Vars["letsencrypt_email"] = "foo@bar.local"
	options.Vars["ingress_gateway_annotations"] = map[string]interface{}{"foo": "bar"}

	defer terraform.Destroy(t, options)
	_, err = terraform.InitAndApplyE(t, options)
	assert.NoError(t, err)
}

func TestApplyAndDestroyWithOnlyPipelines(t *testing.T) {
	_, options, err := getDefaultTerraformOptions(t)
	assert.NoError(t, err)

	options.Vars["cert_manager_namespace"] = "cert-manager"
	options.Vars["istio_operator_namespace"] = "istio-operator"
	options.Vars["istio_namespace"] = "istio-system"
	options.Vars["ingress_gateway_ip"] = "10.20.30.40"
	options.Vars["use_cert_manager"] = true
	options.Vars["install_istio"] = true
	options.Vars["install_cert_manager"] = true
	options.Vars["domain_name"] = "foo.local"
	options.Vars["letsencrypt_email"] = "foo@bar.local"
	options.Vars["ingress_gateway_annotations"] = map[string]interface{}{"foo": "bar"}
	options.Vars["kubeflow_components"] = []string{"'katib'", "'pipelines'"}
	options.Vars["kubeflow_version"] = "1.1.0"

	defer terraform.Destroy(t, options)
	_, err = terraform.InitAndApplyE(t, options)
	assert.NoError(t, err)
}

func TestApplyAndDestroyWithExistingIstioCertManager(t *testing.T) {
	_, options, err := getDefaultTerraformOptions(t)
	istioOptions, err2 := getIstioTerraformOptions(t)
	assert.NoError(t, err)
	assert.NoError(t, err2)

	cmK8sOptions := k8s.NewKubectlOptions("", "", "cert-manager")
	k8s.CreateNamespace(t, cmK8sOptions, "cert-manager")
	defer k8s.DeleteNamespace(t, cmK8sOptions, "cert-manager")

	emptyOptions := &helm.Options{}

	_, err = helm.RunHelmCommandAndGetOutputE(t, emptyOptions, "repo", "add", "jetstack", "https://charts.jetstack.io")
	assert.NoError(t, err)
	_, err = helm.RunHelmCommandAndGetOutputE(t, emptyOptions, "repo", "update")
	assert.NoError(t, err)

	cmOptions := &helm.Options{
		KubectlOptions: cmK8sOptions,
		SetValues: map[string]string{
			"installCRDs": "true",
		},
		Version: "v0.16.1",
	}

	defer helm.Delete(t, cmOptions, "cert-manager", true)
	require.NoError(t, helm.InstallE(t, cmOptions, "jetstack/cert-manager", "cert-manager"))

	options.Vars["ingress_gateway_ip"] = "10.20.30.40"
	options.Vars["use_cert_manager"] = true
	options.Vars["install_istio"] = false
	options.Vars["install_cert_manager"] = false
	options.Vars["domain_name"] = "foo.local"
	options.Vars["letsencrypt_email"] = "foo@bar.local"
	options.Vars["ingress_gateway_annotations"] = map[string]interface{}{"foo": "bar"}

	istioOptions.Vars["ingress_gateway_ip"] = "10.20.30.40"
	istioOptions.Vars["use_cert_manager"] = true
	istioOptions.Vars["domain_name"] = "foo.local"
	istioOptions.Vars["ingress_gateway_annotations"] = map[string]interface{}{"foo": "bar"}

	defer terraform.Destroy(t, istioOptions)
	_, err = terraform.InitAndApplyE(t, istioOptions)
	assert.NoError(t, err)

    time.Sleep(180 * time.Second)

	defer terraform.Destroy(t, options)
	_, err = terraform.InitAndApplyE(t, options)
	assert.NoError(t, err)
}
