from alina.privacy import redact_text


def test_redaction():
    raw="Email jane@example.com about VEGA-123 and ask Jane Doe to review 550e8400-e29b-41d4-a716-446655440000."
    out=redact_text(raw,names=["Jane Doe"])
    assert "jane@example.com" not in out
    assert "VEGA-123" not in out
    assert "Jane Doe" not in out
    assert "550e8400" not in out
