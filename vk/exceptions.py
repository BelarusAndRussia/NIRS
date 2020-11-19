class BaseVkError(Exception):
    pass


class VkApiPrifileIsPrivate(BaseVkError):
    pass


class VkApiToManyExecute(BaseVkError):
    pass


class VkApiTooManySameExecute(BaseVkError):
    pass


class VkApiDeletedUser(BaseVkError):
    pass


class VkApiLimitReached(BaseVkError):
    pass


class VkApiBannedUser(BaseVkError):
    pass