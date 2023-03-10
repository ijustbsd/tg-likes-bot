import factory.fuzzy

from . import models


class TelegramUserFactory(factory.Factory):
    class Meta:
        model = models.TelegramUser

    id = factory.fuzzy.FuzzyInteger(1, 100)
    username = factory.Sequence(lambda x: f"username_{x}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    rating = factory.fuzzy.FuzzyInteger(-42, 42)


class PhotoFactory(factory.Factory):
    class Meta:
        model = models.Photo

    id = factory.fuzzy.FuzzyInteger(1, 100)
    author = factory.SubFactory(TelegramUserFactory)
    likes = factory.fuzzy.FuzzyInteger(0, 10)
    dislikes = factory.fuzzy.FuzzyInteger(-10, 0)
    rating = factory.fuzzy.FuzzyInteger(-42, 42)
    created_at = factory.Faker("date")


class VoteFactory(factory.Factory):
    class Meta:
        model = models.Vote

    user = factory.SubFactory(TelegramUserFactory)
    photo = factory.SubFactory(PhotoFactory)
    value = factory.fuzzy.FuzzyChoice([-1, 1])


class NotificationFactory(factory.Factory):
    class Meta:
        model = models.Notification

    id = factory.fuzzy.FuzzyInteger(1, 100)
    type = factory.fuzzy.FuzzyChoice(models.NotificationType)
    text = factory.fuzzy.FuzzyText()
    parameters: dict = {}
    sent_at = factory.Faker("date")
    created_at = factory.Faker("date")
