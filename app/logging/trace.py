from ddtrace import tracer
from app.config import logCfg

init_called = False

def enabled():
    return logCfg.datadog['tracing']['enabled']

def init():
    global init_called

    if not init_called:
        dd_tracing = logCfg.datadog['tracing']
        tracer.enabled = enabled()

        if tracer.enabled:
            #log.info(f"DataDog tracing: {dd_tracing}")
            tracer.configure(
                https=dd_tracing['https'],
                hostname=dd_tracing['host'],
                port=dd_tracing['port'],
            )

    init_called = True

