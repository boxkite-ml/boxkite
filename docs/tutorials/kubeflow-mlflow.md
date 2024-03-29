# Kubeflow & MLflow

This tutorial shows you how to use Boxkite in the context of a Kubeflow cluster with MLflow.

## Launch the Test Drive

**Note: the test drive doesn't work in Safari yet. Please use Chrome or Firefox for now! Also please note it won't work in Private/Incognito windows.**

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

<iframe width="1024" height="300" id="testdrive" data-src="https://testfaster.ci/launch?embedded=true&repo=https://github.com/boxkite-ml/boxkite&file=examples/kubeflow-mlflow/.testfaster.yml" style="display:none"></iframe>

At busy times, you may need to wait a few minutes for a test drive environment to become available.

**Note that the environment will shut down automatically 1 hour after you start using it.**

If you get a black screen on "Booting VM", please be patient - it's loading. Failing that, scroll down to the bottom of this page to see a video of the demo.

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
  <br/>`quay.io/boxkite/tensorflow-1.15.2-notebook-cpu:8e225af`
  <br/>This preinstalls the required [dependencies](https://github.com/boxkite-ml/boxkite/blob/main/examples/kubeflow-mlflow/custom-jupyter/requirements.txt) and makes the demo notebook available.
* **Workspace Volume:** Tick the "Don't use Persistent Storage for User's home" box. Then click "dismiss" on the warning that pops up. This is so that the demo notebook shows up in your home directory.
* **Configurations:** Click "Configurations" and then select "MLflow". This will set up the notebook environment so that it can talk to MLflow automatically.

Now click the blue "Launch" button at the bottom of the screen.
The notebook server may take a few moments to start up.

## Run demo notebook

Once the notebook server has started, click the "Connect" button.

Open the `demo.ipynb` notebook and click the "play" icon for each of the cells in turn.

This will demonstrate training a model, recording the model and the training data distribution as a histogram to mlflow, then deploying the model, and running a load test against it.

## Inspect the model in MLflow

Click the "MLflow" button in the test drive interface above.
Observe that the model has been recorded in the MLflow model registry along with the histogram.

This is useful so that you can maintain a "model registry" which records which models you've trained along with their training distributions in a central location, for improved collaboration and governance in your team.

## Open Grafana

Click the "Grafana" button in the test drive interface above.

Log into Grafana with:

<div style="margin-left:2em;">
<strong>Username:</strong> admin <br />
<strong>Password:</strong> grafana123
</div>

Click on the **Dashboards icon** on the left (four boxes).

Then click **Manage** -> **MLOps** -> **Model Metrics**.

Observe that the load test you started in the demo notebook is visible in the Grafana dashboard.

This is useful so that you can monitor how the model data and predictions are drifting from what it was trained on.

Note that Grafana here is aggregating the statistics over the _three_ model servers you deployed from the notebook, so it is working in HA mode!


## Notes for advanced users

* You can also use the SSH tab above to poke around the cluster with `kubectl`, etc.
* You can also view the Terraform used for the tutorial environment and to replicate it yourself: <a href="https://github.com/boxkite-ml/boxkite/tree/master/examples/kubeflow-mlflow" target="_blank">Terraform for MLOps stack</a>.


## Demo video

This video shows the above tutorial in action.

<style>
.video-wrapper {
  position: relative;
  display: block;
  height: 0;
  padding: 0;
  overflow: hidden;
  padding-bottom: 56.25%;
  border: 1px solid gray;
}
.video-wrapper > iframe {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>

<div class="video-wrapper">
  <iframe width="1280" height="720" src="https://www.youtube.com/embed/zz-0Yn6_eMQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
