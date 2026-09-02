import sys
import types
from alina.models import SituationAnalysis, SituationInput
from alina.providers.heuristic import HeuristicProvider
from alina.providers.openai_provider import OpenAIProvider


def test_openai_adapter_uses_structured_parse(monkeypatch):
    situation=SituationInput(narrative="The PM committed to Friday. I think the team needs another week. My manager has not said which constraint is fixed.")
    parsed=HeuristicProvider().analyze(situation)
    captured={}

    class FakeCompletions:
        def parse(self, **kwargs):
            captured.update(kwargs)
            message=types.SimpleNamespace(parsed=parsed,refusal=None)
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)])

    class FakeClient:
        def __init__(self, api_key):
            captured["api_key"]=api_key
            self.chat=types.SimpleNamespace(completions=FakeCompletions())

    fake=types.ModuleType("openai")
    fake.OpenAI=FakeClient
    monkeypatch.setitem(sys.modules,"openai",fake)

    p=OpenAIProvider(model="gpt-test",api_key="secret-for-test")
    result=p.analyze(situation)
    assert captured["model"]=="gpt-test"
    assert captured["response_format"] is SituationAnalysis
    assert result.provider=="openai"
    assert result.model=="gpt-test"
