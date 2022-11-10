import enum

from tortoise import fields, models


class ValorantCharacter(models.Model):
    id = fields.CharField(unique=True, max_length=100, pk=True)
    name = fields.CharField(max_length=100)


class ValorantWeapon(models.Model):
    id = fields.CharField(unique=True, max_length=100, pk=True)
    name = fields.CharField(max_length=100)


class ValorantArmor(models.Model):
    id = fields.CharField(unique=True, max_length=100, pk=True)
    name = fields.CharField(max_length=100)


class ValorantPlayer(models.Model):
    puuid = fields.CharField(pk=True, unique=True, max_length=120)
    game_name = fields.CharField(max_length=100)
    tag_line = fields.CharField(max_length=20)

    def __repr__(self):
        return f"<ValorantPLayer {self.game_name}#{self.tag_line}>"

    def __str__(self):
        return f"{self.game_name}#{self.tag_line}"


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


class ValorantTeamPlayer(models.Model):
    game = fields.ForeignKeyField("models.ValorantGame")
    player = fields.ForeignKeyField("models.ValorantPlayer")
    # Red|Blue
    team = fields.CharEnumField(TeamEnum, max_length=20)
    character = fields.ForeignKeyField("models.ValorantCharacter")
    score = fields.IntField()
    rounds = fields.IntField()
    kills = fields.IntField()
    deaths = fields.IntField()
    assists = fields.IntField()
    playtime = fields.IntField()
    grenade_casts = fields.IntField()
    ability1_casts = fields.IntField()
    ability2_casts = fields.IntField()
    ultimate_casts = fields.IntField()

    class Meta:
        unique_together = (("game", "player"),)


class ValorantGameRound(models.Model):
    game = fields.ForeignKeyField("models.ValorantGame")
    round_num = fields.IntField()
    round_result = fields.CharField(max_length=60)
    round_ceremony = fields.CharField(max_length=60)
    winning_team = fields.CharField(max_length=160)
    bomb_planter = fields.ForeignKeyField(
        "models.ValorantTeamPlayer", null=True, related_name="plant_rounds"
    )
    bomb_defuser = fields.ForeignKeyField(
        "models.ValorantTeamPlayer", null=True, related_name="defuse_rounds"
    )
    plant_time = fields.IntField(null=True)
    defuse_time = fields.IntField(null=True)
    plant_location_x = fields.IntField(null=True)
    plant_location_y = fields.IntField(null=True)
    defuse_location_x = fields.IntField(null=True)
    defuse_location_y = fields.IntField(null=True)
    round_result_code = fields.CharField(max_length=60, null=True)

    class Meta:
        unique_together = (
            (
                "game",
                "round_num",
            ),
        )


class ValorantPlayerRoundStat(models.Model):
    player = fields.ForeignKeyField("models.ValorantTeamPlayer")
    round = fields.ForeignKeyField("models.ValorantGameRound")
    score = fields.IntField()
    grenade_effects = fields.IntField(null=True)
    ability1_effects = fields.IntField(null=True)
    ability2_effects = fields.IntField(null=True)
    ultimate_effects = fields.IntField(null=True)
    loadout_value = fields.IntField()
    remaining = fields.IntField()
    spent = fields.IntField()
    weapon = fields.ForeignKeyField("models.ValorantWeapon", null=True)
    armor = fields.CharField(max_length=160, null=True)

    class Meta:
        unique_together = (
            (
                "round",
                "player",
            ),
        )


class ValorantDamageRoundStat(models.Model):
    player_round = fields.ForeignKeyField("models.ValorantPlayerRoundStat")
    receiver = fields.ForeignKeyField(
        "models.ValorantTeamPlayer", related_name="round_damages"
    )
    damage = fields.IntField()
    legshots = fields.IntField()
    bodyshots = fields.IntField()
    headshots = fields.IntField()

    class Meta:
        unique_together = (
            (
                "player_round",
                "receiver",
            ),
        )


class ValorantPlayerRoundKill(models.Model):
    player_round = fields.ForeignKeyField("models.ValorantPlayerRoundStat")
    game_time = fields.IntField()
    round_time = fields.IntField()
    killer = fields.ForeignKeyField(
        "models.ValorantTeamPlayer", related_name="rounds_kill_player"
    )
    victim = fields.ForeignKeyField(
        "models.ValorantTeamPlayer", related_name="rounds_kill_victim"
    )
    victim_location_x = fields.IntField()
    victim_location_y = fields.IntField()
    player_location_x = fields.IntField(null=True)
    player_location_y = fields.IntField(null=True)
    last_hit_damage_item = fields.CharField(max_length=60)
    last_hit_damage_type = fields.CharField(max_length=60)
    last_hit_second_fire_mode = fields.BooleanField()

    class Meta:
        unique_together = (
            (
                "player_round",
                "victim",
            ),
        )


class KillAssist(models.Model):
    round_kill = fields.ForeignKeyField("models.ValorantPlayerRoundKill")
    player = fields.ForeignKeyField("models.ValorantTeamPlayer")


class ValorantLocationData(models.Model):
    x = fields.IntField()
    y = fields.IntField()
