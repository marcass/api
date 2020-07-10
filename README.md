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
```

# IPV6 network

Create using (don't do this, just use a standard network and let nginx handle ipv6)
```
docker network create --subnet=172.18.0.0/16 --gateway=172.18.0.1 --ipv6 --subnet=2001:db8:2::/64 vexme6
```

# Setting up Kong

## Grafana

```
curl -i -X POST http://localhost:8001/services --data name=grafana --data url='http://grafana:3000'
```

```
curl -i -X POST http:/localhost:8001/services/grafana/routes --data 'paths[]=/grafana' --data 'name=grafana'
```

Uses Grafana's auth plugin. Place rate limit on this

```
curl -X POST http://localhost:8001/services/grafana/plugins --data "name=rate-limiting" --data "config.second=5" --data "config.hour=10000" --data "config.policy=local"
```

## auth

```
curl -i -X POST http://localhost:8001/services --data name=auth --data url='http://auth-api:5001'
```

```
curl -i -X POST http:/localhost:8001/services/auth/routes --data 'paths[]=/auth/login' --data 'name=auth' --data 'strip_path=false'
```

## Senor data

```
curl -i -X POST http://localhost:8001/services --data name=data_in --data url='http://sensor-api:5002'
```

```
curl -i -X POST http://localhost:8001/services/data_in/routes --data 'paths[]=/data' --data 'name=data' --data 'strip_path=false'
```

### Tank data

```
curl -i -X POST http://localhost:8001/services --data name=tanks_in --data url='http://tank-ingress-api:5003'
```

```
curl -i -X POST http:/localhost:8001/services/tanks_in/routes --data 'paths[]=/marcus' --data 'name=tank_data' --data 'strip_path=false'
```


## Consumers

* Used for auth of data providers
* Types are:
   * software user
   * site user
   * admin user


```
curl -i -X POST http://localhost:8001/consumers/   --data "username=<username>"
```

```
curl -i -X POST  http://localhost:8001/consumers/<user>/basic-auth --data "username=<user>" --data "password=<pass>"
```

## JWT

### Set up jwt plugin

```
curl -i -X POST localhost:8001/routes/data/plugins --data "name=jwt"
```

### Add to a route

### Disabe

```
curl -i -X PATCH localhost:8001/plugins/fef076d1-9d96-4a82-bab2-e352607df70c --data "enabled=false"
```

### Set up ACL for groups

```
curl -i -X PATCH localhost:8001/plugins/fef076d1-9d96-4a82-bab2-e352607df70c --data "enabled=false"
```

### Add consumer to group

```
curl -X POST http://localhost:8001/consumers/{consumer}/acls --data "group=<group>"
```


### Add a route for retreiving data for consumer


```
curl -i -X POST http://localhost:8001/services --data name=jwt-stuff --data url='http://localhost:8001'
```

```
curl -i -X POST http://localhost:8001/services/jwt-stuff/routes --data 'paths[]=/jwt-stuff' --data 'name=jwt-stuff'
```

```
curl -X POST http://localhost:8001/services/jwt-stuff/plugins --data "name=basic-auth" --data "config.hide_credentials=true"
