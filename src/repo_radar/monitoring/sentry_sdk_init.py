import os, sentry_sdk
def init():
    dsn = os.getenv("SENTRY_DSN")
    if not dsn: 
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT","dev"),
        release=os.getenv("SENTRY_RELEASE"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE","0")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE","0")),
        send_default_pii=False,
    )
