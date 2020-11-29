class BaseVkError(Exception):
    """ Ошибка при работе с ВКонтакте """


class VkApiProfileIsPrivate(BaseVkError):
    """ Профиль пользователя ВК имеет частный доступ """


class VkApiToManyExecute(BaseVkError):
    """ Много запросов """


class VkApiTooManySameExecute(BaseVkError):
    """ Много одинаковых действий """


class VkApiDeletedUser(BaseVkError):
    """ Профиль пользователя ВК удален """


class VkApiLimitReached(BaseVkError):
    """ Превышен лимит запросов """


class VkApiBannedUser(BaseVkError):
    """ Профиль пользователя ВК заблокирован """


class VkInvalidSettings(BaseVkError):
    """ Заданные параметры не корректны """


class VkInvalidToken(BaseVkError):
    """ Токен пользователя не действителен """