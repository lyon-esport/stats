# coding=utf-8
# author Etienne G.
# flake8: noqa

import asyncio
import logging
import sys
from typing import List

from pyot.conf.utils import import_confs
from pyot.core.queue import Queue

# config must be inited before import TODO: check
# noqa: E402
import_confs("les_stats.utils.pyot_config")


from pyot.models import riot, val
from pyot.models.val.content import ContentItemData

logger = logging.getLogger(__name__)


async def last_played_champs(summoner_name: str):
    content = await val.Content().get()
    players: dict[str, ContentItemData] = {x.id.lower(): x for x in content.characters}
    print(players)
    async with Queue() as queue:
        puuid = (
            await riot.account.Account(game_name="FB Elite", tag_line="1TAP")
            .using("val")
            .get()
        )  # .pipeline(ValPipeline)
        puuid = "-OTn0pMDHpo_KJrB7jBPngkltajE-Tz30weC50dCUnZ-4U8pcTyWzyyudgJlsm0DFBBkawdsRfDo1A"
        print(await riot.account.Account(puuid=puuid).using("val").get())
        print(f"PUID: {puuid}")
        print(await val.Match(id="3b07de15-f643-47a0-a9b7-4a86a6d384e9").get())
        history = await val.MatchHistory(puuid=puuid).get()
        for match in history.history[:10]:
            await queue.put(match.get())
        first_10_matches: List[val.Match] = await queue.join()
    champ_names = []
    for match in first_10_matches:
        char = {}
        for participant in match.players:
            char[participant.puuid] = players[participant.character_id]
            print(
                f"{participant.team_id} - {participant.game_name} - {participant.party_id}"
            )
            if participant.puuid == puuid:
                champ_names.append(participant.character_id)
        for result in match.round_results:
            print("Match: {}".format(result.round_num))
            print("\tresult: {}".format(result.round_result))
            print("\tPlayers:")
            for p in result.player_stats:
                print(
                    "\t\t{} - kills: {} - damage: {}".format(
                        char[p.puuid].name,
                        ", ".join(
                            ["{}".format(char[x.victim_puuid].name) for x in p.kills]
                        ),
                        ", ".join(
                            [
                                "{}({})".format(char[x.receiver].name, x.damage)
                                for x in p.damage
                            ]
                        ),
                    )
                )
            # print("Defuse : {} {}".format(test.defuse_location.x, test.defuse_location.y))
            # print(test.bomb_defuser_puuid)
            # print(await riot.Account(puuid=test.bomb_defuser_puuid).using("val").get())
    return [players[x].name for x in champ_names]


if __name__ == "__main__":
    print("Summoner name:", sys.argv[1])
    last_played_champ_names = asyncio.run(last_played_champs(sys.argv[1]))
    print(
        "Last played champ names (last 10 matches):",
        last_played_champ_names,
    )
