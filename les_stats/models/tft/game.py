from tortoise import fields, models

from les_stats.schemas.riot.game import RiotHost


class TFTGame(models.Model):
    match_id = fields.CharField(pk=True, max_length=200)
    data_version = fields.CharField(max_length=200)
    game_datetime = fields.DatetimeField()
    game_length = fields.FloatField()
    game_version = fields.CharField(max_length=200)
    queue_id = fields.IntField()
    tft_set_number = fields.IntField()
    tft_game_type = fields.CharField(max_length=200)
    tft_set_core_name = fields.CharField(max_length=200, default="")
    event = fields.ForeignKeyField(
        "models.Event", related_name="event", on_delete="CASCADE", null=True
    )
    tournament = fields.ForeignKeyField(
        "models.Tournament", related_name="tournament", on_delete="CASCADE", null=True
    )
    stage = fields.ForeignKeyField(
        "models.Stage", related_name="stage", on_delete="CASCADE", null=True
    )

    def __str__(self):
        return self.match_id


class TFTPlayer(models.Model):
    puuid = fields.CharField(max_length=200)
    region: RiotHost = fields.CharEnumField(RiotHost)

    def __str__(self):
        return f"region:{self.region}, puuid:{self.puuid}"

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
        "models.TFTCompanion", related_name="participant"
    )
    player = fields.ForeignKeyField("models.TFTPlayer", related_name="participant")
    game = fields.ForeignKeyField("models.TFTGame", related_name="participant")
    augments = fields.ManyToManyField(
        "models.TFTAugment",
        related_name="augments",
        through="participant_augment",
    )

    def __str__(self):
        return self.id


class TFTCompanion(models.Model):
    content_id = fields.CharField(pk=True, max_length=200)
    skin_id = fields.IntField()
    species = fields.CharField(max_length=200)

    def __str__(self):
        return self.content_id


class TFTAugment(models.Model):
    name = fields.CharField(pk=True, max_length=200)

    def __str__(self):
        return self.name


class TFTTrait(models.Model):
    name = fields.CharField(pk=True, max_length=200)

    def __str__(self):
        return self.name


class TFTCurrentTrait(models.Model):
    id = fields.IntField(pk=True)
    num_units = fields.IntField()
    style = fields.IntField()
    tier_current = fields.IntField()
    tier_total = fields.IntField()
    trait = fields.ForeignKeyField("models.TFTTrait", related_name="current_trait")
    participant = fields.ForeignKeyField(
        "models.TFTParticipant", related_name="current_trait"
    )

    def __str__(self):
        return self.id


class TFTUnit(models.Model):
    character_id = fields.CharField(pk=True, max_length=200)

    def __str__(self):
        return self.character_id


class TFTCurrentUnit(models.Model):
    id = fields.IntField(pk=True)
    chosen = fields.CharField(max_length=200, default="")
    name = fields.CharField(max_length=200)
    rarity = fields.IntField()
    tier = fields.IntField()
    items = fields.ManyToManyField(
        "models.TFTItem", related_name="items", through="unit_item"
    )
    unit = fields.ForeignKeyField("models.TFTUnit", related_name="current_unit")
    participant = fields.ForeignKeyField("models.TFTParticipant", related_name="unit")

    def __str__(self):
        return self.name


class TFTItem(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, default="")

    def __str__(self):
        return f"id:{self.id}, name:{self.name if self.name else 'None'}"
