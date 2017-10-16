FROM alpine:3.6

RUN apk update \
    && apk upgrade \
    && apk add python py2-pip

COPY . /mha

RUN pip install --no-cache-dir -r /mha/requirements.txt

WORKDIR /mha
EXPOSE 8080
CMD ["/usr/bin/python", "/mha/server.py", "-b", "0.0.0.0"]
