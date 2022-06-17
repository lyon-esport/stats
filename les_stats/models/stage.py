from tortoise import fields, models


class Stage(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name
