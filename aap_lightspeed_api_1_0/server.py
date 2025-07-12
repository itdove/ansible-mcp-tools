from os import environ
from urllib.parse import urljoin

from mcp.server.fastmcp.utilities.logging import get_logger, configure_logging

from ansible_mcp_tools.service import AAPRegistry

from ansible_mcp_tools.openapi.tool_rules import (
    MethodRule,
    OperationIdBlackRule,
    NoDescriptionRule,
)
from ansible_mcp_tools.server import LightspeedOpenAPIAAPServer
from ansible_mcp_tools.openapi.spec_loaders import FileLoader

from ansible_mcp_tools.authentication import LightspeedAuthenticationBackend
from ansible_mcp_tools.authentication.validators.aap_token_validator import (
    AAPTokenValidator,
)
from ansible_mcp_tools.authentication.validators.aap_jwt_validator import (
    AAPJWTValidator,
)

logger = get_logger(__name__)

configure_logging("DEBUG")

SERVICE_NAME="lightspeed"
AAP_GATEWAY_URL = environ.get("AAP_GATEWAY_URL")
AAP_SERVICE_URL = environ.get("AAP_SERVICE_URL")
URL = environ.get("OPENAPI_SPEC_URL")
HOST = environ.get("HOST", "127.0.0.1")
PORT = environ.get("PORT", 8004)

logger.info(f"AAP_GATEWAY_URL: {AAP_GATEWAY_URL}")
logger.info(f"AAP_SERVICE_URL: {AAP_SERVICE_URL}")
logger.info(f"OPENAPI_SPEC_URL: {URL}")
logger.info(f"HOST: {HOST}")
logger.info(f"PORT: {PORT}")

registry = AAPRegistry()

service = registry.get_targeted_service(SERVICE_NAME)
validation_url = urljoin(service.targeted_services_url[SERVICE_NAME],service.validation_uri)

mcp = LightspeedOpenAPIAAPServer(
    name="AAP Lightspeed API 1.0 MCP Server",
    service_name=SERVICE_NAME,
    service=service,
    auth_backend=LightspeedAuthenticationBackend(
        authentication_validators=[
            AAPJWTValidator(validation_url, verify_cert=False),
            AAPTokenValidator(validation_url, verify_cert=False),
        ]
    ),
    spec_loader=registry.get_targeted_service(SERVICE_NAME).get_open_api_document_loader(),
    tool_rules=[
        MethodRule(["PUT", "OPTIONS", "DELETE", "PATCH"]),
        OperationIdBlackRule(
            [
                "ai_chat_create",
                "ai_feedback_create",
                "telemetry_settings_set",
                "wca_api_key_set",
                "wca_model_id_set",
                "ai_completions_create",
            ]
        ),
        NoDescriptionRule(),
    ],
    host=HOST,
    port=PORT,
)

if __name__ == "__main__":
    mcp.run(transport="sse")
