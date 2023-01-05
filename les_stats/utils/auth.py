import hashlib
import secrets
import string
from functools import wraps
from typing import List

import asyncclick as click
from fastapi import Header, HTTPException
from tortoise.exceptions import DoesNotExist

from les_stats.models.internal.auth import Api, Scope
from les_stats.utils.config import get_settings
from les_stats.utils.db import close_db, init_db

API_KEY_SIZE_MIN = 50
API_KEY_SIZE_MAX = 64


def get_digest(x_api_key: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha512", x_api_key.encode(), get_settings().SALT.encode(), 1000
    )
    return digest.hex()


async def is_api_key_scope_valid(api_key: str, scopes: List[Scope]) -> bool:
    try:
        api_obj = await Api.get(api_key=get_digest(api_key))
    except DoesNotExist:
        return False
    return api_obj.scope in scopes


def scope_required(scopes: List[Scope]):
    def wrapper(func):
        @wraps(func)
        async def wrap(request, *args, **kwargs):
            if not await is_api_key_scope_valid(
                request.headers.get("x-api-key"), scopes
            ):
                raise HTTPException(status_code=403, detail="X-Api-Key header invalid")

            return await func(request, *args, **kwargs)

        return wrap

    return wrapper


async def verify_api_key(x_api_key: str = Header()):
    if (
        x_api_key is None
        or await Api.filter(api_key=get_digest(x_api_key)).count() != 1
    ):
        raise HTTPException(status_code=403, detail="X-Api-Key header invalid")
    return x_api_key


@click.group()
async def auth() -> None:
    await init_db()


@auth.result_callback()
async def process_result(result, **kwargs):
    await close_db()


@click.command()
@click.option(
    "--scope",
    default=Scope.read.name,
    help=f'API Key scope ({",".join([e.value for e in Scope])})',
)
@click.argument("name")
async def create_api_key(name: str, scope: str) -> None:
    if len(name) == 0:
        raise click.BadParameter("Name can't be empty")

    if scope not in Scope.__members__:
        raise click.BadParameter("Invalid scope")

    alphabet = string.ascii_letters + string.digits + string.punctuation
    api_key = "".join(
        secrets.choice(alphabet)
        for _ in range(
            secrets.SystemRandom().randint(API_KEY_SIZE_MIN, API_KEY_SIZE_MAX - 1)
        )
    )
    await Api.create(name=name, api_key=get_digest(api_key), scope=scope)

    click.secho(api_key, fg="green")


@click.command()
async def list_api_key() -> None:
    apis_obj = await Api.all()

    if len(apis_obj) == 0:
        click.secho("No API Key exist", fg="yellow")
    else:
        for api_obj in apis_obj:
            click.secho(api_obj, fg="green")


@click.command()
@click.argument("name")
async def delete_api_key(name: str) -> None:
    if len(name) == 0:
        raise click.BadParameter("NAME can't be empty")

    deleted_count = await Api.filter(name=name).delete()
    if not deleted_count:
        raise click.BadParameter("NAME not found")
    else:
        click.secho("API key deleted", fg="green")


auth.add_command(create_api_key)
auth.add_command(list_api_key)
auth.add_command(delete_api_key)


if __name__ == "__main__":
    auth(_anyio_backend="asyncio")
