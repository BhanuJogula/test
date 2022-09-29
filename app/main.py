import app.openapi as openapi
import os
import importlib

from .logger import log
from fastapi import FastAPI
from app.config import logCfg, httpCfg
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.ip_restrict_middleware import IpRestrictMiddlware
from app.middleware.logger import LoggerMiddleware
from ddtrace.contrib.asgi import TraceMiddleware
from app.init import init as app_init
from app.logging.trace import enabled as trace_enabled


restrict_ips = False
debug_headers = logCfg.get('debug_headers', -1)
log_pretty_json = logCfg.get('pretty_json', -1)
# multiple origins can be separated by comma
origins_csv = httpCfg.cors_origins
origins = [o.strip() for o in origins_csv.split(',')]

app = FastAPI()
app.add_middleware(LoggerMiddleware, debug_headers=debug_headers, pretty_json=log_pretty_json)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if restrict_ips:
    app.add_middleware(IpRestrictMiddlware)

app.openapi_schema = openapi.load()

log.info("Loading routes...")
cur_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
for subdir, dirs, files in os.walk(os.path.join(cur_dir, "routers")):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(subdir, file).replace(".py", "").replace(cur_dir, "app").replace("/", ".").replace("\\", ".")
            module = importlib.import_module(full_path)
            app.include_router(module.router)
            log.info(full_path.replace("routers.", ""))


app_init()
if trace_enabled():
    app = TraceMiddleware(app)