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

# Accessing influx on host machine

1 Install influxdb-client
1 Communication defaults to localhost and docker container port on influx is forwarded

## list databases

```
influx -execute 'SHOW DATABASES'
```

## show the series in a database

```
influx -database sensors -execute 'SHOW SERIES'
```

## retrun some stuff

```
influx -database sensors -execute 'SELECT * FROM "7_days"."things"'
```

## running test image of influx

```
docker run --rm --network=influx -p 8088:8088 -p 8086:8086 -e INFLUXDB_BIND_ADDRESS=":8088" -v /mnt/influx:/var/lib/influxdb influxdb:latest
```

# Dealing with Kong form command line

* Use curl

 ```
 curl -i --user <user>:<pass> url
 ```

 ```
 curl -H 'Accept: application/json' -H "Authorization: Bearer ${TOKEN}" url
 ```

 Querieying Kong for stuff:
 ```
 curl localhost:8001/routes | python -m json.tool
'''
