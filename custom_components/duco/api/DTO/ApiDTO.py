from dataclasses import dataclass


@dataclass
class ApiInfoDTO:
    Url: str
    QueryParameters: list[str]
    Methods: list[str]
    Modules: list[str] | None = None


@dataclass
class ApiDetailsDTO:
    ApiVersion: str
    PublicApiVersion: str
    ApiInfo: list[ApiInfoDTO]
