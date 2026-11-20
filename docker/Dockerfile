FROM alpine:3.22

# Instalar utilidades SQLite3 y Python3 estándar
RUN apk add --no-cache sqlite python3

WORKDIR /app
COPY sql_server.py /app/sql_server.py

ENV DB_PATH=/data/us_accidents.db

# Volumen persistente para la base de datos
VOLUME /data

EXPOSE 8090

CMD ["python3", "/app/sql_server.py"]
