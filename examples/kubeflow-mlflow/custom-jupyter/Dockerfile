FROM gcr.io/kubeflow-images-public/tensorflow-1.15.2-notebook-cpu:1.0.0
USER root
RUN pip install mlflow sklearn boxkite dataclasses boto3
RUN chown jovyan /home/jovyan
USER jovyan
ENV cache-bust "2021-04-29 06:59:00"
RUN cd /home/jovyan; git clone https://github.com/boxkite-ml/boxkite; ln -s boxkite/examples/kubeflow-mlflow/demo.ipynb demo.ipynb
