from app.config import Settings


def test_settings_accept_generated_env_fields():
    settings = Settings(
        database_url="postgresql://user:pass@localhost:5432/airpuff",
        timescaledb_url="postgresql://user:pass@localhost:5432/airpuff",
        redis_url="redis://localhost:6379",
        google_client_id="google-client",
        google_client_secret="google-secret",
        apple_client_id="apple-client",
        apple_client_secret="apple-secret",
        oidc_issuer="https://auth-dev.cloudpuff.org/realms/cloudpuff",
        oidc_client_id="airpuff-web",
        oidc_client_secret="oidc-secret",
        oidc_redirect_uri="https://dev.airpuff.info/api/v1/auth/oidc/callback",
        oidc_admin_roles="admin,airpuff-admin",
        session_secret="dev-session-secret",
        base_url="https://dev.airpuff.info",
        fli_rite_base_url="https://dev.fli-rite.net",
        grafana_url="http://localhost:3000",
        grafana_username="admin",
        grafana_password="admin",
        secret_key="dev-secret-key",
        algorithm="HS256",
        access_token_expire_minutes=30,
        environment="development",
        debug=True,
        log_level="INFO",
        host="0.0.0.0",
        port=25080,
        workers=2,
        max_requests=1000,
        max_requests_jitter=100,
    )

    assert settings.oidc_issuer == "https://auth-dev.cloudpuff.org/realms/cloudpuff"
    assert settings.base_url == "https://dev.airpuff.info"
    assert settings.fli_rite_base_url == "https://dev.fli-rite.net"
    assert settings.session_secret == "dev-session-secret"
