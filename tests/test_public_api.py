"""Contract tests for the public BOA API."""

import pytest

from boa_bigapi import (
    BOA,
    BOAContext,
    ComputeBackend,
    CPUWorkflow,
    Prismatics,
    Transport,
    Workflow,
)


class Component:
    def process(self, data):
        return f"{data}-processed"


class Backend(ComputeBackend):
    def execute(self, operation):
        return {"operation": operation}


class TestTransport(Transport):
    def send(self, packet, destination=None):
        return packet, destination

    def receive(self, source=None):
        return source


def test_public_imports():
    assert all((BOA, BOAContext, CPUWorkflow, ComputeBackend, Prismatics, Transport, Workflow))


def test_context_create():
    context = BOAContext.create("payload", {"source": "test"})
    assert context.payload == "payload"
    assert context.metadata == {"source": "test"}
    assert context.request_id
    assert context.timestamp


def test_context_replace_preserves_identity_and_merges_metadata():
    context = BOAContext.create("one", {"source": "test"})
    replaced = context.replace("two", stage="next")
    assert replaced.payload == "two"
    assert replaced.request_id == context.request_id
    assert replaced.timestamp == context.timestamp
    assert replaced.metadata == {"source": "test", "stage": "next"}


def test_cpu_workflow_chains_components():
    result = CPUWorkflow([Component(), Component()]).execute("input")
    assert result.payload == "input-processed-processed"


def test_cpu_workflow_rejects_invalid_component():
    with pytest.raises(TypeError, match=r"process\(data\)"):
        CPUWorkflow().use(object())


def test_boa_compute_delegates_to_backend():
    assert BOA(backend=Backend()).compute("op") == {"operation": "op"}


def test_boa_compute_requires_backend():
    with pytest.raises(RuntimeError, match="No compute backend configured"):
        BOA().compute("op")


def test_abstract_backend_and_transport_contracts():
    with pytest.raises(TypeError):
        ComputeBackend()
    with pytest.raises(TypeError):
        Transport()

    transport = TestTransport()
    assert transport.send("packet", "destination") == ("packet", "destination")
    assert transport.receive("source") == "source"
