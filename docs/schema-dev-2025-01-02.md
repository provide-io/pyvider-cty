

Schema work:
🏗️🐍 pyvider: cty, tests, and schema - 2024-12-28-13:11
iteration: 8c

Major DSL work.

## examples

services = tfobj({ # or maybe tfschema(tfobj(. dunno.
    "frontend": tfobj({
        "url": tfstr(required=True),
        "port": tfnum(required=True, default=443)
    }, required=True),
    "backend": tfobj({
        "url": tfstr(required=True),
        "port": tfnum(required=True, default=8080),
        "api_versions": tfobj({
            "v1": tfstr(required=True, validators=["minmax"]),
            "v2": tfstr(),  # Optional by default
            "v3": tfstr(computed=True)
        }, required=True)
    }, required=True)
}, required=True)

###

@attrs.define
class AppConfigSchema(Schema):
    feature_flags = tfobj({
        "enable_beta": CtyBool(required=True, default=False),
        "dark_mode": CtyBool(computed=True),
        "new_ui": CtyBool(required=True, default=True)
    }, required=True)

    scaling_config = tfobj({
        "max_instances": tfnum(required=True, default=10),
        "min_instances": tfnum(required=True, default=1),
        "auto_scaling": CtyBool(required=True, default=True)
    }, required=True)

    services = tfobj({
        "frontend": tfobj({
            "url": tfstr(required=True),
            "port": tfnum(required=True, default=443),
            "enable_cache": CtyBool(default=False)
        }, required=True),
        "backend": tfobj({
            "url": tfstr(required=True),
            "port": tfnum(required=True, default=8080),
            "api_versions": tfobj({
                "v1": tfstr(required=True),
                "v2": tfstr(),
                "v3": tfstr(computed=True)
            }, required=True),
            "cache_ttl": tfnum(sensitive=True, default=300)
        }, required=True)
    }, required=True)

    database = tfobj({
        "db_name": tfstr(required=True),
        "username": tfstr(required=True),
        "password": tfstr(required=True, sensitive=True),
        "replicas": tfnum(default=3),
        "maintenance_window": tfstr(optional=True, default="Sunday 2am-4am")
    }, required=True)

    monitoring = tfobj({
        "enabled": CtyBool(default=True),
        "level": tfstr(default="info"),
        "slack_webhook": tfstr(sensitive=True)
    }, computed=True)

    secrets = tfobj({
        "api_key": tfstr(required=True, sensitive=True),
        "jwt_secret": tfstr(required=True, sensitive=True),
        "encryption_key": tfstr(required=True, sensitive=True)
    }, required=True, sensitive=True)
