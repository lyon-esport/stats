from tortoise import fields, models


class Event(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    tournaments = fields.ManyToManyField(
        "models.Tournament", related_name="tournaments", through="event_tournament"
    )

    def __str__(self) -> str:
        return self.name
