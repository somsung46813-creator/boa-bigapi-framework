"""Contract tests for the backend-neutral Prismatics API."""

from boa_bigapi.prismatics import Prismatics


class MockBackend:
    def __init__(self):
        self.calls = []

    def execute(self, operations):
        self.calls.append(list(operations))
        return operations


def test_prismatics_preserves_operation_order_and_delegates():
    backend = MockBackend()
    gpu = Prismatics(backend)

    result = (
        gpu.pitch(45)
        .roll(30)
        .index([0, 1, 2])
        .scatter([10, 20, 30])
        .compute()
    )

    expected = [
        ("pitch", 45),
        ("roll", 30),
        ("index", [0, 1, 2]),
        ("scatter", [10, 20, 30]),
    ]
    assert result == expected
    assert backend.calls == [expected]


def test_prismatics_accepts_backend_class():
    class Backend(MockBackend):
        pass

    gpu = Prismatics(Backend)
    gpu.pitch(10)

    assert gpu.compute() == [("pitch", 10)]
