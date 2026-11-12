from ecommerce_ai.config.settings import Settings


def test_langsmith_defaults_are_defined():
    settings = Settings()

    assert settings.langsmith_api_key == ""
    assert settings.langsmith_project == "multi-ai-agent"
    assert settings.langsmith_tracing is True


def test_cookie_samesite():
    s_secure = Settings(auth_cookie_secure=True, auth_cookie_samesite="none")
    assert s_secure.cookie_samesite == "none"

    s_insecure = Settings(auth_cookie_secure=False, auth_cookie_samesite="none")
    assert s_insecure.cookie_samesite == "lax"
