from fastapi import APIRouter  # , Query, Request, Response

# from typing import Dict, List
# from les_stats.models.internal.auth import Scope
# from les_stats.models.valorant.game import ValorantCharacter
# from les_stats.schemas.client_api.data import DataResponse, ErrorResponse
# from les_stats.utils.auth import scope_required

router = APIRouter()


# @router.get("/by-puuid", response_model=List[DataResponse])
# @scope_required([Scope.read, Scope.write])
# async def get_player_name_from_puuid(
#     request: Request, response: Response, encrypted_puuid: List[str] = Query()
# ):
#     players = await ValorantCharacter.all()
#     if not players:
#         response.status_code = 404
#         return DataResponse(
#             data={}, error=ErrorResponse(status_code=404, message="Player not found")
#         )
#     return DataResponse(data={})
#
#
# @router.get("/by-name", response_model=List[DataResponse])
# @scope_required([Scope.read, Scope.write])
# async def get_summoners_puuid_from_name(
#     request: Request, response: Response, summoner_name: List[str] = Query()
# ):
#     response.status_code, data = await RiotAPI(RiotGame.tft).get_summoners_puuid(
#         summoner_name
#     )
#     return data
