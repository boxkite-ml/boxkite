FROM python:3.8.4

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY serve_completed.py /app/serve_completed.py

ENV FLASK_APP serve_completed.py

CMD ["flask", "run", "--host=0.0.0.0"]
