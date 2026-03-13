"""Constants for the BASE Belgium integration."""

DOMAIN = "base_belgium"

CONF_PHONE = "phone"

# BASE/Telenet API URLs
BASE_API = "https://api.prd.base.be"
BASE_OCAPI = f"{BASE_API}/ocapi"
BASE_OCAPI_PUBLIC = f"{BASE_OCAPI}/public"
BASE_OCAPI_PUBLIC_API = f"{BASE_OCAPI_PUBLIC}/api"
BASE_OCAPI_OAUTH = f"{BASE_OCAPI}/oauth"
BASE_OPENID = "https://login.prd.base.be/openid"
BASE_SECURE = "https://secure.base.be"

# Endpoints
URL_USERDETAILS = f"{BASE_OCAPI_OAUTH}/userdetails"
URL_AUTHORIZATION = f"{BASE_OCAPI}/login/authorization/base_be"
URL_INTROSPECT = f"{BASE_SECURE}/idp/idx/introspect"
URL_IDENTIFY = f"{BASE_SECURE}/idp/idx/identify"
URL_CHALLENGE = f"{BASE_SECURE}/idp/idx/challenge"
URL_CHALLENGE_ANSWER = f"{BASE_SECURE}/idp/idx/challenge/answer"
URL_FINGERPRINT = f"{BASE_SECURE}/auth/services/devicefingerprint"
URL_DEVICE_NONCE = f"{BASE_SECURE}/api/v1/internal/device/nonce"
URL_MOBILE_SUBS = f"{BASE_OCAPI_PUBLIC_API}/product-service/v1/product-subscriptions"
URL_MOBILE_USAGE = f"{BASE_OCAPI_PUBLIC_API}/mobile-service/v3/mobilesubscriptions"
URL_PRODUCT_SPEC = f"{BASE_API}/omapi/public/product"
URL_ALIAS_LOOKUP = "https://cf-alias-prd.ciam-prod.awsprod.external.telenet.be/base/alias/lookup"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 240  # 4 hours in minutes
MIN_SCAN_INTERVAL = 60  # 1 hour minimum
MAX_SCAN_INTERVAL = 1440  # 24 hours maximum
