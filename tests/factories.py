from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Union

import factory
from django.conf import settings
from faker import Faker

from django_flex_reviews import models

fake = Faker()


class FactoryParam(Enum):
    UNSET_COMPLETED_AT = "UNSET_COMPLETED_AT"


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyFunction(fake.unique.name)
    email = factory.LazyFunction(fake.unique.email)
    is_staff = False

    class Meta:
        model = settings.AUTH_USER_MODEL


class ReviewFactory(factory.django.DjangoModelFactory):
    """
    kwargs:
        completed_at: optional datetime that will be broken out into
          completed_at_day, completed_at_month, completed_at_year.

    Examples:
        Use today's date in completed_at* fields.
        r = ReviewFactory(completed_at=datetime.now())

        Set all completed_at* fields to None.
        r = ReviewFactory(completed_at=None)

        Set approximate date.
        r = ReviewFactory(completed_at_month=1, completed_at_year=1999)

        Let Faker choose a random date for you.
        r = ReviewFactory()
    """

    user = factory.SubFactory(UserFactory)

    @classmethod
    def _adjust_completed_at(cls, **kwargs):
        completed_at: Union[
            Optional[datetime], Literal[FactoryParam.UNSET_COMPLETED_AT]
        ] = kwargs.get("completed_at")

        unset_completed_at: bool = completed_at == FactoryParam.UNSET_COMPLETED_AT
        unset_completed_at_fields: bool = (
            "completed_at_day" not in kwargs
            and "completed_at_month" not in kwargs
            and "completed_at_year" not in kwargs
        )

        # If any completed_at* fields are set, then don't adjust them.
        if not unset_completed_at_fields:
            return kwargs

        # If any "completed_at" is explicitly set to None, then allow completed_at*
        # fields to be blank.
        if completed_at is None:
            return kwargs

        # If "completed_at" is unset and the completed_at fields are also unset, then
        # fill in faker date values for them.
        if unset_completed_at and unset_completed_at_fields:
            completed_at = fake.date_time()

        kwargs["completed_at_day"] = completed_at.day
        kwargs["completed_at_month"] = completed_at.month
        kwargs["completed_at_year"] = completed_at.year

        return kwargs

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        kwargs = cls._adjust_completed_at(**kwargs)
        return kwargs

    class Meta:
        model = models.Review

    class Params:
        completed_at: Union[
            Optional[datetime], Literal[FactoryParam.UNSET_COMPLETED_AT]
        ] = FactoryParam.UNSET_COMPLETED_AT
