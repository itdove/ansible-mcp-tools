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

    def __init__(self,name,string_to_replace_in_path, targeted_service_url,open_api_document_url,gateway_base_path,service_base_path):
        super().__init__(name,string_to_replace_in_path, targeted_service_url,open_api_document_url)
        self.gateway_base_path=gateway_base_path
        self.service_base_path=service_base_path

    @override
    def build_path(self, path: str) -> str:
        path = path.lstrip("/")
        return path.lstrip(self.gateway_base_path)

@dataclass
class AAPRegistry(BaseRegistry):
    def __init__(self):
        super().__init__()
        self.register_aap_services()

    def register_aap_services(self):
        self.register_targeted_service(
            AAPService(
                name="gateway",
                string_to_replace_in_path=None,
                gateway_base_path="api/gateway",
                service_base_path="api/gateway",
                targeted_service_url={"gateway":environ.get("AAP_GATEWAY_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL")
            )
        )
        self.register_targeted_service(
            AAPService(
                name="controller",
                string_to_replace_in_path=None,
                gateway_base_path="api/controller",
                service_base_path="api",
                targeted_service_url={"gateway":environ.get("AAP_GATEWAY_URL"),
                                    "controller":environ.get("AAP_CONTROLLER_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL")
            )
        )
        self.register_targeted_service(
            AAPService(
                name="lightspeed",
                string_to_replace_in_path=None,
                gateway_base_path="api/lightspeed",
                service_base_path="api",
                targeted_service_url={"gateway":environ.get("AAP_GATEWAY_URL"),
                                    "controller":environ.get("AAP_CONTROLLER_URL")},
                open_api_document_url=environ.get("OPENAPI_SPEC_URL")
            )
        )

    @override
    def build_api_url(self,
        service_name: str,  path: str, **kwargs
    ) -> str | None:
        base_url_path = self.get_aap_service_url_base_path_by_header_name(
            service_name, kwargs["auth_header_name"]
        )
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
        service_name: str, auth_header_name: str
    ) -> str | None:
        if auth_header_name != AAP_JWT_HEADER_NAME:
            return self.get_aap_service_url_base_path(service_name, context="gateway")
        return self.get_aap_service_url_base_path(service_name)

    def get_aap_service_url_base_path(self, service_name: str, context: str = None) -> str | None:
        service_url = self.get_targeted_service_url(service_name)
        if service_url is None:
            return None
        service = self.get_targeted_service_url(service_name)
        if service is None:
            return None
        base_path = service.service_base_path
        if context == "gateway":
            service_url = self.get_targeted_service_url(context)
            base_path = service.gateway_base_path
        return urljoin(service_url, base_path)





