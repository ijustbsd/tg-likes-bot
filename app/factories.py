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
