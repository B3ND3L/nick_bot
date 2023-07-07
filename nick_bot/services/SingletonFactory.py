from nick_bot.datas.OverwatchDB import OverwatchDB


class SingletonFactory:

    """
    Singleton factory
    """

    __instance = None

    @staticmethod
    def get_overwatch_db_instance(config) -> OverwatchDB:
        """
        Get the instance of the OverwatchDB
        :param config:
        :return:
        """
        if SingletonFactory.__instance is None:
            SingletonFactory.__instance = OverwatchDB(config)
        return SingletonFactory.__instance
            