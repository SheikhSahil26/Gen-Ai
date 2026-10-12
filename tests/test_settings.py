from ecommerce_ai.config.settings import Settings


def test_langsmith_defaults_are_defined():
    settings = Settings()

    assert settings.langsmith_api_key == ""
    assert settings.langsmith_project == "multi-ai-agent"
    assert settings.langsmith_tracing is True
