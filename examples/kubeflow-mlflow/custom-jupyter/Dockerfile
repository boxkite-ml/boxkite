FROM gcr.io/kubeflow-images-public/tensorflow-1.15.2-notebook-cpu:1.0.0
USER root
RUN pip install mlflow sklearn boxkite dataclasses boto3
RUN chown jovyan /home/jovyan
USER jovyan
ENV cache-bust "2021-04-28 08:08:13"
RUN cd /home/jovyan; git clone https://github.com/boxkite-ml/docs; ln -s docs/examples/kubeflow-mlflow/demo.ipynb demo.ipynb
