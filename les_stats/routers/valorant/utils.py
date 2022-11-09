# coding=utf-8
# author Etienne G.

import logging

from pyot.models import val
from pyot.models.val import Match

from les_stats.models.valorant.game import (
    KillAssist,
    ValorantCharacter,
    ValorantGame,
    ValorantGameRound,
    ValorantPlayer,
    ValorantPlayerRoundKill,
    ValorantPlayerRoundStat,
    ValorantTeamPlayer,
    ValorantWeapon,
)

logger = logging.getLogger(__name__)


async def get_match_stats(match_id):
    match_data = await val.Match(match_id)
    await insert_match_data(match_data)


async def insert_match_data(match: Match):
    # Skip non defuse game
    if not match.info.game_mode.startswith("/Game/GameModes/Bomb/"):
        print("Not defuse")
        return
    print(match.id)
    # print(match.start_time_millis)
    # Create match in DB
    match_db, _ = await ValorantGame.update_or_create(
        match_id=match.id,
        defaults={
            "start_time": match.info.start,
            "length": match.info.length.total_seconds(),
            "map_url": match.info.map_url,
            "is_completed": match.info.is_completed,
            "game_mode": match.info.game_mode,
        },
    )

    # Process players
    for participant in match.players:
        account = await participant.account.get()

        player, _ = await ValorantPlayer.get_or_create(
            puuid=account.puuid,
            defaults={"game_name": account.game_name, "tag_line": account.tag_line},
        )
        character = await ValorantCharacter.get(id=participant.character_id)

        game_player, _ = await ValorantTeamPlayer.get_or_create(
            game=match_db,
            player=player,
            defaults={
                "team": participant.team_id,
                "character": character,
                "score": participant.stats.score,
                "rounds": participant.stats.rounds_played,
                "kills": participant.stats.kills,
                "deaths": participant.stats.deaths,
                "assists": participant.stats.assists,
                "playtime": participant.stats.playtime.total_seconds(),
                "grenade_casts": participant.stats.ability_casts.grenade_casts,
                "ability1_casts": participant.stats.ability_casts.ability1_casts,
                "ability2_casts": participant.stats.ability_casts.ability2_casts,
                "ultimate_casts": participant.stats.ability_casts.ultimate_casts,
            },
        )

    # Process round stats
    for match_round in match.round_results:
        bomb_defuser = None
        bomb_planter = None

        if match_round.bomb_defuser_puuid:
            bomb_defuser = await ValorantTeamPlayer.get(
                game=match_db,
                player__puuid=match_round.bomb_defuser_puuid,
            )

        if match_round.bomb_planter_puuid:
            bomb_planter = await ValorantTeamPlayer.get(
                game=match_db,
                player__puuid=match_round.bomb_planter_puuid,
            )

        db_round, _ = await ValorantGameRound.get_or_create(
            game=match_db,
            round_num=match_round.round_num,
            defaults={
                "round_result": match_round.round_result,
                "round_ceremony": match_round.round_ceremony,
                "winning_team": match_round.winning_team,
                "bomb_planter": bomb_planter,
                "bomb_defuser": bomb_defuser,
                "plant_time": match_round.plant_round_time.total_seconds(),
                "defuse_time": match_round.defuse_round_time.total_seconds(),
                "plant_location_x": match_round.plant_location.x
                if match_round.plant_location
                else None,
                "plant_location_y": match_round.plant_location.y
                if match_round.plant_location
                else None,
                "defuse_location_x": match_round.defuse_location.x
                if match_round.defuse_location
                else None,
                "defuse_location_y": match_round.defuse_location.y
                if match_round.defuse_location
                else None,
                "round_result_code": match_round.round_result,
            },
        )

        # Process player round stats
        for player_stats in match_round.player_stats:
            player = await ValorantTeamPlayer.get(
                game=match_db, player__puuid=player_stats.puuid
            )
            weapon = None
            if player_stats.economy.weapon_id:
                weapon = await ValorantWeapon.get(
                    id=player_stats.economy.weapon_id.lower()
                )

            player_round_stat, _ = await ValorantPlayerRoundStat.get_or_create(
                player=player,
                round=db_round,
                defaults={
                    "score": player_stats.score,
                    "grenade_effects": player_stats.ability.grenade_effects,
                    "ability1_effects": player_stats.ability.ability1_effects,
                    "ability2_effects": player_stats.ability.ability2_effects,
                    "ultimate_effects": player_stats.ability.ultimate_effects,
                    "loadout_value": player_stats.economy.loadout_value,
                    "remaining": player_stats.economy.remaining,
                    "spent": player_stats.economy.spent,
                    "weapon": weapon,
                },
            )
            for kill in player_stats.kills:
                killer = await ValorantTeamPlayer.get(
                    game=match_db, player__puuid=kill.killer_puuid
                )

                victim = await ValorantTeamPlayer.get(
                    game=match_db, player__puuid=kill.victim_puuid
                )
                round_kill, _ = await ValorantPlayerRoundKill.update_or_create(
                    player_round=player_round_stat,
                    victim=victim,
                    killer=killer,
                    defaults={
                        "game_time": kill.game_time.total_seconds(),
                        "round_time": kill.round_time.total_seconds(),
                        "victim_location_x": kill.victim_location.x,
                        "victim_location_y": kill.victim_location.y,
                        "player_location_x": kill.player_locations[0].location.x
                        if kill.player_locations
                        else None,
                        "player_location_y": kill.player_locations[0].location.y
                        if kill.player_locations
                        else None,
                        "last_hit_damage_item": kill.finishing_damage.damage_item,
                        "last_hit_damage_type": kill.finishing_damage.damage_type,
                        "last_hit_second_fire_mode": kill.finishing_damage.is_secondary_fire_mode,
                    },
                )
                for assist in kill.assistants:
                    assist_player = await ValorantTeamPlayer.get(
                        game=match_db, player__puuid=assist.puuid
                    )
                    round_kill, _ = await KillAssist.get_or_create(
                        round_kill=round_kill, player=assist_player
                    )
