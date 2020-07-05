import asyncio
import json
import pymongo
import redis
import opentracing
import logging
import time
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
from jaeger_client import Config

async def run(loop):
    #=============== configuracion con servidor de nats ===============
    await nc.connect(servers=["http://35.223.171.148:4222"])
    future = asyncio.Future()
    #=============== configuracion con servidor de jaeguer ============
    config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': "34.72.72.45",
                'reporting_port': 5775,
            },
            'logging': True,
        },
        service_name='my-app',
    )
    tracer = config.initialize_tracer()
    with opentracing.tracer.start_span('Datos_BDS') as span:
        # ======== enviando datos a mongo ================
        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            #aca se empizan a enviar los datos a las bases de datos
            con=pymongo.MongoClient('34.70.196.45',27017)
            with opentracing.tracer.start_span('Datos_Mongo',child_of=span) as span_mongo:
                try:
                    db=con.proyecto2
                    db.casos.insert({"name":data["name"],"depto":data["depto"],"age":data["age"],"form":data["form"],"state":data["state"]})
                    print("datos enviados a mongo")
                    span_mongo.log_event('send data mongo', payload=data)
                except Exception as e:
                    span_mongo.set_tag('send data mongo', 'Failure')
                    print(e)
                    print("problemas con la conexion de mongo")
                finally:
                    con.close()
        #print(data)
            with opentracing.tracer.start_span('Datos_Redis',child_of=span) as span_redis:
                # ======== enviando datos a redis ================
                try:
                    r = redis.Redis(host='34.70.196.45',port=6379)
                    r.rpush('proyecto2','{"name" : "'+data["name"]+'", "depto" : "'+data["depto"]+'", "age" :'+str(data["age"])+', "form" : "'+data["form"]+'", "state" : "'+data["state"]+'"}')
                    print("datos enviados a redis")
                    span_redis.log_event('send data redis', payload=data)
                except Exception as e:
                    span_redis.set_tag('send data redis', 'Failure')
                    print(e)
                    print("hay problemas en la conexion con redis")
                print(data)
        await nc.subscribe("updates", cb=message_handler)

if __name__ == '__main__':
    nc = NATS()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()
