from tortoise import fields, models

from les_stats.models.internal.event import Event


class Tournament(models.Model):
    name = fields.CharField(pk=True, max_length=200)
    stages = fields.ManyToManyField(
        "models.Stage", related_name="stages", through="tournament_stage"
    )
    events: fields.ReverseRelation[Event]

    def __str__(self) -> str:
        return self.name
