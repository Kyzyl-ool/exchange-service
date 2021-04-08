FROM python:latest

COPY requirements.txt /tmp
COPY victor /tmp/victor
COPY setup.py /tmp
COPY wsgi.py /tmp
COPY app.py /tmp

WORKDIR /tmp

RUN pip install -r requirements.txt

CMD ["python", "wsgi.py"]

EXPOSE 5000