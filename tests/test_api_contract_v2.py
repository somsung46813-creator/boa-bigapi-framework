"""Acceptance tests for the public BOA API contract."""

import pytest

from boa_bigapi import BOA, BOAContext, CPUWorkflow


class Double:
    def process(self, value):
        return value * 2


class AddOne:
    def process(self, value):
        return value + 1


def test_context_create_and_replace_preserve_identity_and_merge_metadata():
    context = BOAContext.create({"value": 10}, metadata={"source": "test"})
    updated = context.replace({"value": 21}, stage="cpu")

    assert updated.request_id == context.request_id
    assert updated.timestamp == context.timestamp
    assert updated.metadata == {"source": "test", "stage": "cpu"}
    assert updated.payload == {"value": 21}


def test_cpu_workflow_processes_payload_and_preserves_context():
    workflow = CPUWorkflow().use(Double()).use(AddOne())

    result = workflow.execute(10)

    assert isinstance(result, BOAContext)
    assert result.payload == 21


def test_boa_facade_delegates_to_workflow():
    workflow = CPUWorkflow().use(Double()).use(AddOne())
    boa = BOA(workflow=workflow)

    result = boa.execute(10)

    assert isinstance(result, BOAContext)
    assert result.payload == 21


def test_boa_requires_backend_for_compute():
    with pytest.raises(RuntimeError, match="No compute backend configured"):
        BOA().compute("operation")
