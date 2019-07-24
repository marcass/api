# api

This project is aimed at rapid redeplyoment of microservices when a machine falls over with a view to hosting eslewhere if necessary

## Structure

* Kong api gateway
* Konga front end for Kong
* Python3 flask api's
* ingress from mqtt and https
* reporting via web interface via gateways/api's

## Deployment

### Kong/konga

Deploy images via docker compose and have a persistent kong data store (back this up)
* Seperate network to data store for sensors

### Sensor datastore

* Using influx db
* Influx and pyhton3 gunicorn served api's on same network
* mounted volume for backups of datastore with influxdb

### Webserver

* Nginx (local installation)
