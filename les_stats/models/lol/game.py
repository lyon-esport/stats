from tortoise import fields, models


class LOLGame(models.Model):
    match_id = fields.CharField(pk=True, max_length=200)
