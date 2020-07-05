
import asyncio
import requests
import json
import pymongo
import redis
import opentelemetry.ext.requests
from opentelemetry import trace
from opentelemetry.ext import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="Envio-Datos-BDS", agent_host_name="simplest-agent.default.svc.cluster.local", agent_port=6831
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(jaeger_exporter)
)

opentelemetry.ext.requests.RequestsInstrumentor().instrument()

async def run(loop):
    await nc.connect(servers=["http://35.223.171.148:4222"])
    future = asyncio.Future()

    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        #aca se empizan a enviar los datos a las bases de datos
        con=pymongo.MongoClient('35.238.115.111',27017)
        try:
            db=con.proyecto2
            db.casos.insert({"name":data["name"],"depto":data["depto"],"age":data["age"],"form":data["form"],"state":data["state"]})
            print("datos enviados a mongo")
            with tracer.start_as_current_span("Mongo"):
                span = tracer.get_current_span()
                span.set_attribute(data, True)
        except Exception as e:
            print(e)
            print("problemas con la conexion de mongo")
            span = tracer.get_current_span()
                span.set_attribute(e, True)
        finally:
            con.close()
        #print(data)
        # ======== enviando datos a redis ================
        try:
            r = redis.Redis(host='35.238.115.111',port=6379)
            r.rpush('proyecto2','{"name" : "'+data["name"]+'", "depto" : "'+data["depto"]+'", "age" :'+str(data["age"])+', "form" : "'+data["form"]+'", "state" : "'+data["state"]+'"}')
            print("datos enviados a redis")
            with tracer.start_as_current_span("redis"):
                span = tracer.get_current_span()
                span.set_attribute(data, True)
        except Exception as e:
            print(e)
            print("hay problemas en la conexion con redis")
            span = tracer.get_current_span()
            span.set_attribute(e, True)
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
