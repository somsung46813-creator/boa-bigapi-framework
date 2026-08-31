"""Focused integration tests for the CPU workflow facade."""

from boa_bigapi import BOA, BOAContext, CPUWorkflow


class AppendComponent:
    def __init__(self, suffix: str):
        self.suffix = suffix

    def process(self, data: str) -> str:
        return f"{data}{self.suffix}"


def test_cpu_workflow_empty_pipeline_wraps_input_in_context():
    result = CPUWorkflow().execute("input")

    assert isinstance(result, BOAContext)
    assert result.payload == "input"
    assert result.request_id
    assert result.timestamp


def test_cpu_workflow_executes_single_component():
    result = CPUWorkflow([AppendComponent("-A")]).execute("input")

    assert result.payload == "input-A"


def test_cpu_workflow_chains_components_in_order():
    workflow = CPUWorkflow().use(AppendComponent("-A")).use(AppendComponent("-B"))

    result = workflow.execute("input")

    assert result.payload == "input-A-B"


def test_cpu_workflow_preserves_context_identity_metadata():
    context = BOAContext.create("input", {"source": "test"})

    result = CPUWorkflow([AppendComponent("-A")]).execute(context)

    assert result.request_id == context.request_id
    assert result.timestamp == context.timestamp
    assert result.metadata == context.metadata
    assert result.payload == "input-A"


def test_cpu_workflow_rejects_invalid_component():
    workflow = CPUWorkflow()

    try:
        workflow.use(object())
    except TypeError as exc:
        assert "process(data)" in str(exc)
    else:
        raise AssertionError("CPUWorkflow accepted a component without process")


def test_boa_execute_delegates_to_cpu_workflow():
    workflow = CPUWorkflow([AppendComponent("-A")])
    boa = BOA(workflow=workflow)

    result = boa.execute("input")

    assert result.payload == "input-A"
