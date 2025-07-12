import types

from dataclasses import dataclass
from ansible_mcp_tools.openapi.spec_loaders import BaseLoader, FileLoader, UrlLoader
from urllib.parse import urljoin

@dataclass
class BaseService:
    name: str
    targeted_services_url: dict[str:str]
    open_api_document_url: str
    validation_uri: str
 
    def __init__(self, name,targeted_services_url,open_api_document_url,validation_uri):
        self.name = name
        self.targeted_services_url = targeted_services_url
        self.open_api_document_url = open_api_document_url
        self.validation_uri = validation_uri

    def get_open_api_document_loader(self) -> BaseLoader:
        print(f"open_api_document_url: {self.open_api_document_url}")
        if self.open_api_document_url.lower().startswith("file://"):
            return FileLoader(self.open_api_document_url)
        return UrlLoader(self.open_api_document_url)

    def build_path(self, path: str) -> str:
        return path

    def api_url_builder(self,path: str, **kwargs) -> str | None:
        return urljoin(self.targeted_services_url,self.build_path(path))

@dataclass
class BaseRegistry:
    # targeted_services_registry: dict = field(default_factory=dict[str:BaseService])
    targeted_services_registry: dict[str:BaseService]

    def __init__(self):
        self.targeted_services_registry = {}

    def register_targeted_service(self,service: BaseService) -> None:
        self.targeted_services_registry[service.name] = service

    def get_targeted_service(self,name: str) -> BaseService | None:
        return self.targeted_services_registry.get(name, None)
