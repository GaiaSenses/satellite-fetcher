FROM python:slim-bullseye

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
ARG PORT=8080
ENV PORT=${PORT}

EXPOSE $PORT
CMD gunicorn -b :${PORT} server:app
