from boa_bigapi import BOA, BOAContext, CPUWorkflow


class AddOne:
    def process(self, data):
        return data + 1


def test_context_preserves_request_id_and_metadata():
    context = BOAContext(1, request_id="req-1", metadata={"source": "test"})
    updated = context.replace(2, stage="AddOne")
    assert updated.request_id == "req-1"
    assert updated.payload == 2
    assert updated.metadata == {"source": "test", "stage": "AddOne"}


def test_cpu_workflow_returns_context():
    result = CPUWorkflow().use(AddOne()).execute(1)
    assert isinstance(result, BOAContext)
    assert result.payload == 2


def test_boa_facade_delegates_to_workflow():
    result = BOA(CPUWorkflow().use(AddOne())).execute(4)
    assert result.payload == 5
