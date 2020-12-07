import environ


secret_file = environ.secrets.INISecrets( "APP_SECRETS_INI", "src/web/secret.env")


@environ.config
class AppConfig:
    metrichost = environ.var()

    @environ.config
    class BotConfig:
        host = environ.var()
        anominterval = environ.var(converter=int)
        forecastinterval = environ.var(converter=int)

    bot = environ.group(BotConfig)

    @environ.config
    class ServerConfig:
        modelp1 = environ.var()
        modelp2 = environ.var()

        db_string = secret_file.secret()

        @environ.config
        class LoaderConfig:
            sensorfile = environ.var()
            apiurl = environ.var()
            sensortimeinterval = environ.var(converter=int)
            weatherurl = environ.var()
            mosecomurl = environ.var()

        loader = environ.group(LoaderConfig)
    server = environ.group(ServerConfig)
