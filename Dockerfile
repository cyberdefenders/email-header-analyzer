FROM python:3-alpine

WORKDIR /usr/src/mha

COPY requirements.txt ./
RUN apk add --no-cache gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt

COPY mha/ .

EXPOSE 8080

ENTRYPOINT ["python", "/usr/src/mha/server.py", "-b", "0.0.0.0"]
