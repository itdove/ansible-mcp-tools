
from dataclasses import dataclass, field
from ansible_mcp_tools.openapi.spec_loaders import BaseLoader, FileLoader, UrlLoader

@dataclass
class BaseService:
    name: str
    string_to_replace_in_path: dict
    targeted_services_url: dict[str:str]
    open_api_document_url: str

    def __init__(self, name, string_to_replace_in_path,targeted_services_url,open_api_document_url):
        self.name = name
        self.string_to_replace_in_path= string_to_replace_in_path
        self.targeted_services_url = targeted_services_url
        self.open_api_document_url = open_api_document_url

    def get_open_api_document_loader(self) -> BaseLoader:
        if self.open_api_document_url.lower().startswith("file://"):
            return FileLoader(self.open_api_document_url)
        return UrlLoader(self.open_api_document_url)

    def build_path(self, path: str) -> str:
        pass

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

    def get_targeted_service_url(self,name: str) -> str | None:
        return self.targeted_services_registry[name].targeted_service_url

    def build_api_url(self,
        service_name: str,  path: str, **kwargs
    ) -> str | None:
        pass
