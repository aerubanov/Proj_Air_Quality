import environ


secret_file = environ.secrets.INISecrets.from_path_in_env("APP_SECRETS_INI", "src/web/secret.ini")


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

        dbstring = secret_file.secret()

        @environ.config
        class LoaderConfig:
            sensorfile = environ.var()
            apiurl = environ.var()
            sensortimeinterval = environ.var(converter=int)
            weatherurl = environ.var()
            mosecomurl = environ.var()
            weathermaxcol = environ.var(converter=int)

        loader = environ.group(LoaderConfig)
    server = environ.group(ServerConfig)
