FROM influxdb:latest
RUN mkdir -p /backup
COPY ./influx/* /backup/
CMD influxd restore -portable -database sensors -host 172.20.0.2:8088 /backup/
