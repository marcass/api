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
* allow kong to access network for api's and datastore, as well as kong-net for it's own stuff

### Sensor datastore

* Using influx db
* Influx and pyhton3 gunicorn served api's on same network
* mounted volume for backups of datastore with influxdb

### Webserver

* Nginx (local installation)
   * reroutes all api requests through to kong
   * knog redirects all traffic to relevant api from there after auth is successful

# Accessing influx on host machine (may exclude once auth sorted)

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

## return some stuff

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

# IPV6 network

Create using 
'''
docker network create --subnet=172.18.0.0/16 --gateway=172.18.0.1 --ipv6 --subnet=2001:db8:2::/64 vexme6
'''
