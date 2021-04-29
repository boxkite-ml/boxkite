# Kubeflow & MLflow

This tutorial shows you how to use Boxkite in the context of a Kubeflow cluster with MLflow.

## Easy Test Drive

**Note: the test drive doesn't work in Safari yet. Please use Chrome or Firefox for now!**

Use the following test drive to launch a temporary Kubernetes cluster with the tutorial running in it:

<script>
function toggle(el) {
  var x = document.getElementById(el);
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
</script>

<a id="button" class="md-button md-button--primary" href="javascript:void(0);" onclick="document.getElementById('testdrive').src=document.getElementById('testdrive').getAttribute('data-src'); toggle('testdrive'); toggle('button')">Launch Test Drive</a>

<iframe width="1024" height="600" id="testdrive" data-src="https://testfaster.ci/launch?embedded=true&repo=https://github.com/boxkite-ml/boxkite&file=examples/kubeflow-mlflow/.testfaster.yml" style="display:none"></iframe>

## Launch the Test Drive

Click the button above to launch the test drive environment.

At busy times, you may need to wait a few minutes for a test drive environment to become available.

(If you get a black screen on "Booting VM", just be patient).

TODO: on black screen, show position in queue.

## Start Kubeflow Notebook Server

Click the "Kubeflow" button inside the test drive frame, and you should see a "CoreOS" login screen (this is the default Kubeflow "dex" login screen). You may want to arrange this tutorial window side by side with the Kubeflow one so that you can easily follow along.

Log into Kubeflow with:

<div style="margin-left:2em;">
<strong>Username:</strong> admin@kubeflow.org <br />
<strong>Password:</strong> 12341234
</div>

Click the "burger bar" (three lines) if necessary, and navigate to to _Notebook Servers_.

Click "+ New Server".

Change the following settings from the defaults:

* **Name:** Name the notebook server anything you like, such as `test`
* **Image:** Tick the "Custom image" checkbox and enter:
  <br/>`quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:428a007
  <br/>This preinstalls the required [dependencies](https://github.com/boxkite-ml/boxkite/blob/main/examples/kubeflow-mlflow/custom-jupyter/requirements.txt) and makes the demo notebook available.
* **Workspace Volume:** Tick the "Don't use Persistent Storage for User's home" box. Then click "dismiss" on the warning that pops up. This is so that the demo notebook shows up in your home directory.
* **Configurations:** Click "Configurations" and then select "MLflow". This will set up the notebook environment so that it can talk to MLflow automatically.

Now click the blue "Launch" button at the bottom of the screen.
The notebook server may take a few moments to start up.

TODO: insert screenshot "this is what it should look like".

## Run demo notebook

Once the notebook server has started, click the "Connect" button.

Open the `demo.ipynb` notebook and click the "play" icon for each of the cells in turn.

This will demonstrate training a model, recording the model and the training data distribution as a histogram to mlflow, then deploying the model, and running a load test against it.

## Inspect the model in MLflow

Click the "MLflow" button in the test drive interface above.
Observe that the model has been recorded in the MLflow model registry along with the histogram.

This is useful so that you can maintain a "model registry" which records which models you've trained along with their training data in a central location, for improved collaboration and governance in your team.

## Open Grafana

Click the "Grafana" button in the test drive interface above.

Observe that the load test you started in the demo notebook is visible in the Grafana dashboard.

This is useful so that you can monitor how the model data and predictions are drifting from what it was trained on.

TODO: make replicas=3 to demonstrate the HA model server stats aggregation selling point.
