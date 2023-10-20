from peewee import (
    Model,
    CharField,
    DateField,
    BooleanField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
)
from installies.models.base import BaseModel
from installies.models.user import User

class VoteJunction(BaseModel):
    """A junction model between votes and an object that needs to be voted on."""

    score = IntegerField(default=0)
    
    def upvote(self, user: User):
        """
        Adds an upvote by the given user.

        Also updates the score field.
        """
        if self.has_user_voted(user) is False:
            return
        
        Vote.create(
            user=user,
            group=self,
            is_upvote=True,
        )

        # updates the vote count
        self.score = self.get_score()
        self.save()

    def downvote(self, user: User):
        """
        Adds an downvote by the given user.

        Also updates the score field.
        """
        if self.has_user_voted(user) is False:
            return
        
        Vote.create(
            user=user,
            group=self,
            is_upvote=False,
        )

        # updates the vote count
        self.score = self.get_score()
        self.save()

    def remove_vote(self, user: User):
        """
        Removes a vote by a user.

        Also updates the score field.
        """
        vote = self.votes.where(Vote.user == user).get().delete_instance()

        # updates the vote count
        self.script = self.get_score()
        self.save()

        return vote

    def has_user_voted(self, user: User):
        """Checks if a given user has voted."""
        return self.votes.where(Vote.user == user).exists()

    def get_score(self):
        """Gets the sum of all the votes (upvotes - downvotes)."""
        return (
            self.votes.where(Vote.is_upvote is True).count() -
            self.votes.where(Vote.is_upvote is False).count()
        )
        
    
class Vote(BaseModel):
    """A model for storing a vote."""

    user = ForeignKeyField(User, backref="votes")
    group = ForeignKeyField(VoteJunction, backref="votes", on_delete='CASCADE')
    is_upvote = BooleanField() #true if upvote, false if downvote
