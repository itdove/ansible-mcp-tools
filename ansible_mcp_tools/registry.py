from os import environ

from urllib.parse import urljoin

from dataclasses import dataclass
from .base_registry import BaseRegistry, BaseService
from typing import override

AAP_JWT_HEADER_NAME = "X-DAB-JW-TOKEN"

@dataclass
class AAPService(BaseService):
    gateway_base_path: str
    service_base_path: str

    def __init__(self,name, targeted_service_url, open_api_document_url, service_base_path, validation_uri, gateway_base_path=None):
        super().__init__(name, targeted_service_url, open_api_document_url, validation_uri)
        self.gateway_base_path=gateway_base_path
        self.service_base_path=service_base_path

    @override
    def build_path(self, path: str) -> str:
        path = path.lstrip("/")
        return path.lstrip(self.gateway_base_path)
    
    @override
    def api_url_builder(self, registry: BaseRegistry, path: str, **kwargs) -> str | None:
        print(f"self: {self}")
        path = self.build_path(path)
        base_url_path = self.get_aap_service_url_base_path_by_header_name(
            self.name, registry, kwargs["header_name"]
        )
        print(f"base_url_path: {base_url_path}")
        if base_url_path is None:
            return None
        for text in ("api/", "/api/"):
            if path.startswith(text):
                path = path[len(text) :]
                break

        if path.startswith("/"):
            path = path[1:]

        return f"{base_url_path}/{path}"

    def get_aap_service_url_base_path_by_header_name(self, 
        service_name: str,registry: BaseRegistry, auth_header_name: str
    ) -> str | None:
        if auth_header_name != AAP_JWT_HEADER_NAME and service_name != "controller24":
            return self.get_aap_service_url_base_path(service_name, registry, context="gateway")
        return self.get_aap_service_url_base_path(service_name, registry)

    def get_aap_service_url_base_path(self, service_name: str, registry: BaseRegistry, context: str = None) -> str | None:
        print(f"context: {context}")
        service_url = self.targeted_services_url[service_name]
        if service_url is None:
            return None
        service = registry.get_targeted_service(service_name)
        if self is None:
            return None
        base_path = self.service_base_path
        if context == "gateway":
            service = registry.get_targeted_service(context)
            service_url = service.targeted_services_url[context]
            base_path = self.gateway_base_path
        print(f"service_url: {service_url} base_path:{base_path}")
        return urljoin(service_url, base_path)

@dataclass
class AAPRegistry(BaseRegistry):
    def __init__(self):
        super().__init__()
        self.register_aap_services()

    def register_aap_services(self):
        self.register_targeted_service(
            AAPService(
                name="gateway",
                gateway_base_path="api/gateway",
                service_base_path="api/gateway",
                targeted_service_url={"gateway":environ.get("AAP_GATEWAY_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL"),
                validation_uri="api/gateway/v1/me/"
            )
        )
        self.register_targeted_service(
            AAPService(
                name="controller24",
                service_base_path="api",
                targeted_service_url={"controller24":environ.get("AAP_SERVICE_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL"),
                validation_uri="api/v2/me/"
            )
        )
        self.register_targeted_service(
            AAPService(
                name="controller",
                gateway_base_path="api/controller",
                service_base_path="api",
                targeted_service_url={"gateway":environ.get("AAP_GATEWAY_URL"),
                                    "controller":environ.get("AAP_SERVICE_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL"),
                validation_uri="api/gateway/v1/me/"
            )
        )
        self.register_targeted_service(
            AAPService(
                name="lightspeed",
                gateway_base_path="api/lightspeed",
                service_base_path="api",
                targeted_service_url={"gateway":environ.get("AAP_GATEWAY_URL"),
                                    "controller":environ.get("AAP_SERVICE_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL"),
                validation_uri="api/gateway/v1/me/"
            )
        )





