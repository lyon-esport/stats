from enum import Enum

from tortoise import fields, models


class Scope(str, Enum):
    read = "read"
    write = "write"


class Api(models.Model):
    api_key = fields.CharField(pk=True, max_length=200)
    name = fields.CharField(unique=True, max_length=200, null=False)
    scope: Scope = fields.CharEnumField(Scope, default=Scope.read)

    def __str__(self) -> str:
        return f"name: {self.name}, scope: {self.scope.value}"
