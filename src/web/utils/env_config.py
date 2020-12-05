import environ


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
        database = environ.var()
        modelp1 = environ.var()
        modelp2 = environ.var()

        @environ.config
        class LoaderConfig:
            sensorfile = environ.var()
            apiurl = environ.var()
            sensortimeinterval = environ.var(converter=int)
            weatherurl = environ.var()
            mosecomurl = environ.var()

        loader = environ.group(LoaderConfig)
    server = environ.group(ServerConfig)
