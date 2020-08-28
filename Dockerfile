FROM python:3.8.2-alpine as build-deps

WORKDIR usr/src/neuron
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Secret Access Keys
ENV AWS_ACCESS_KEY_ID=AKIAW3YQHFS33IF3EIO5
ENV AWS_SECRET_ACCESS_KEY=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

# copy and run the source code
COPY . /neuron
WORKDIR /neuron

EXPOSE 5000
CMD ["gunicorn",  "-w", "5", "-b", "0.0.0.0:5000", "wsgi:app"]
