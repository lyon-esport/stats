from tortoise import fields, models

from les_stats.schemas.riot.game import RiotHost


class TFTGame(models.Model):
    match_id = fields.CharField(pk=True, max_length=200)
    data_version = fields.CharField(max_length=200)
    game_datetime = fields.IntField()
    game_length = fields.FloatField()
    game_version = fields.CharField(max_length=200)
    queue_id = fields.IntField()
    tft_set_number = fields.IntField()
    tft_game_type = fields.CharField(max_length=200)
    tft_set_core_name = fields.CharField(max_length=200, default="")


class TFTPlayer(models.Model):
    puuid = fields.CharField(max_length=200)
    region: RiotHost = fields.CharEnumField(RiotHost)

    class Meta:
        unique_together = ("puuid", "region")


class TFTParticipant(models.Model):
    id = fields.IntField(pk=True)
    gold_left = fields.IntField()
    last_round = fields.IntField()
    level = fields.IntField()
    placement = fields.IntField()
    players_eliminated = fields.IntField()
    time_eliminated = fields.FloatField()
    total_damage_to_players = fields.IntField()
    companion = fields.ForeignKeyField(
        "models.TFTCompanion", related_name="tftparticipant"
    )
    player = fields.ForeignKeyField("models.TFTPlayer", related_name="tftparticipant")
    game = fields.ForeignKeyField("models.TFTGame", related_name="tftparticipant")
    augments = fields.ManyToManyField(
        "models.TFTAugment",
        related_name="tftaugments",
        through="tftparticipant_tftaugment",
    )


class TFTCompanion(models.Model):
    content_id = fields.CharField(pk=True, max_length=200)
    skin_id = fields.IntField()
    species = fields.CharField(max_length=200)


class TFTAugment(models.Model):
    name = fields.CharField(pk=True, max_length=200)


class TFTTrait(models.Model):
    name = fields.CharField(pk=True, max_length=200)


class TFTCurrentTrait(models.Model):
    id = fields.IntField(pk=True)
    num_units = fields.IntField()
    style = fields.IntField()
    tier_current = fields.IntField()
    tier_total = fields.IntField()
    trait = fields.ForeignKeyField(
        "models.TFTTrait", related_name="tftcurrent_tfttrait"
    )
    participant = fields.ForeignKeyField(
        "models.TFTParticipant", related_name="tftcurrent_tfttrait"
    )


class TFTUnit(models.Model):
    character_id = fields.CharField(pk=True, max_length=200)


class TFTCurrentUnit(models.Model):
    id = fields.IntField(pk=True)
    chosen = fields.CharField(max_length=200, default="")
    name = fields.CharField(max_length=200)
    rarity = fields.IntField()
    tier = fields.IntField()
    items = fields.ManyToManyField(
        "models.TFTItem", related_name="tftitems", through="tftunit_tftitem"
    )
    unit = fields.ForeignKeyField("models.TFTUnit", related_name="tftcurrent_tftunit")
    participant = fields.ForeignKeyField(
        "models.TFTParticipant", related_name="tftunit"
    )


class TFTItem(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, default="")
