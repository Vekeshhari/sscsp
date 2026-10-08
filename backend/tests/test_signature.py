from app.services.signer import sign, verify


def test_signature_round_trip():
    payload = 'artifact-123'
    sig = sign(payload)
    assert sig
    assert verify(payload, sig)
    assert not verify(payload + 'x', sig)
