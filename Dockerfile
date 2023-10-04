FROM continuumio/miniconda3

WORKDIR /app

COPY requirements.txt ./
RUN conda install --yes python=3.11 pip gdal pandas
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
ARG PORT=8080
ENV PORT=${PORT}

EXPOSE $PORT
CMD gunicorn -b :${PORT} -t 200 server:app
