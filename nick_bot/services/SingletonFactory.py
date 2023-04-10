from nick_bot.datas.OverwatchDB import OverwatchDB


class SingletonFactory:

    __instance = None

    @staticmethod
    def get_overwatch_db_instance(config) -> OverwatchDB:
        if SingletonFactory.__instance is None:
            SingletonFactory.__instance = OverwatchDB(config)
        return SingletonFactory.__instance
            