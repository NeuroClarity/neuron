FROM python:3.8.2-alpine as base

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

# Install dependencies:
COPY requirements.txt .
RUN source /opt/venv/bin/activate && pip install -r requirements.txt

# need to download the model weights

COPY . /neuron
WORKDIR /neuron

CMD []
