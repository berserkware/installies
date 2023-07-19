from peewee import (
    ForeignKeyField,
)
from installies.models.base import BaseModel
from installies.models.user import User


class Maintainers(BaseModel):
    """A junction model between Maintainer models and maintainable objects."""

    def get_maintainers(self):
        """
        Gets all the maintainers.
        """

        return self.maintainers
    
    def add_maintainer(self, user: User):
        """
        Adds a maintainer.

        Returns the new Maintainer object.
        """

        maintainer = Maintainer.create(user=user, group=self)

        return maintainer

    def remove_maintainer(self, user: User):
        """
        Removes a maintainer.

        If the given user is not a maintainer, nothing happens.
        """

        if self.is_maintainer(user):
            maintainer = (
                Maintainer.select()
                .where(Maintainer.user == user)
                .where(Maintainer.group == self)
                .get()
            )
            maintainer.delete_instance()

    def is_maintainer(self, user: User):
        """Checks if the given user is a maintainer."""

        maintainer = (
            Maintainer
            .select()
            .where(Maintainer.user == user)
            .where(Maintainer.group == self)
        )
        
        if maintainer.exists():
            return True

        return False

    def delete_instance(self):
        for maintainer in self.maintainers:
            maintainer.delete_instance()

        super().delete_instance()


class Maintainer(BaseModel):
    """A model for storing maintainer data."""

    user = ForeignKeyField(User, backref="maintains")
    group = ForeignKeyField(Maintainers, backref="maintainers")
