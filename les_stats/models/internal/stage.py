from tortoise import fields, models

from les_stats.models.internal.tournament import Tournament


class Stage(models.Model):
    name = fields.CharField(pk=True, max_length=200)
    tournaments: fields.ReverseRelation[Tournament]

    def __str__(self) -> str:
        return self.name
