from tortoise import fields, models


class Tournament(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    stages = fields.ManyToManyField(
        "models.Stage", related_name="stages", through="tournament_stage"
    )

    def __str__(self) -> str:
        return self.name
