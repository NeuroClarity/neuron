FROM python:3.8

WORKDIR usr/src/neuron
COPY requirements.txt .

RUN pip3 install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY wsgi.py app ./

# Secret Access Keys
ENV AWS_ACCESS_KEY_ID=AKIAW3YQHFS33IF3EIO5
ENV AWS_SECRET_ACCESS_KEY=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

EXPOSE 5000
CMD ["gunicorn",  "-w", "5", "-b", "0.0.0.0:5000", "wsgi:app"]
