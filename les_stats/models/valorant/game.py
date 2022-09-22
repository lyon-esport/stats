import enum

from tortoise import fields, models


class ValorantCharacter(models.Model):
    character_id = fields.CharField(unique=True, max_length=100)
    name = fields.CharField(max_length=100)


class ValorantPlayer(models.Model):
    puuid = fields.CharField(pk=True, unique=True, max_length=120)
    game_name = fields.CharField(max_length=100)
    tag_line = fields.CharField(max_length=20)


class ValorantGame(models.Model):
    match_id = fields.CharField(pk=True, max_length=200)
    start_time = fields.DatetimeField()
    length = fields.BigIntField()
    map_url = fields.CharField(max_length=200)
    is_completed = fields.BooleanField()
    game_mode = fields.CharField(max_length=200)


class TeamEnum(enum.Enum):
    red = "Red"
    blue = "Blue"


class ValorantTeam(models.Model):
    game = fields.ForeignKeyField("models.ValorantGame")
    player = fields.ForeignKeyField("models.ValorantPlayer")
    # Red|Blue
    team = fields.CharEnumField(TeamEnum, max_length=20)
