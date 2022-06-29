from tortoise import fields, models


class Player(models.Model):
    puuid = fields.CharField(pk=True, max_length=200)

    def __str__(self) -> str:
        return self.puuid
