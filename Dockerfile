FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir '.[all]'
ENV ALINA_DB=/data/alina.db
VOLUME ["/data"]
EXPOSE 8787
CMD ["alina", "serve", "--host", "0.0.0.0", "--port", "8787"]
