from pca.core.events import AgentEvent, TraceContext


def test_trace_context_new_generates_non_empty_trace_id():
    """测试 TraceContext.new() 会生成非空 trace_id。"""
    trace = TraceContext.new()

    assert trace.trace_id
    assert isinstance(trace.trace_id, str)


def test_agent_event_stores_event_type_trace_id_and_payload():
    """测试 AgentEvent 能保存事件类型、trace_id 和结构化 payload。"""
    event = AgentEvent(
        event_type="tool.started",
        trace_id="trace-123",
        payload={"tool_name": "read_file"},
    )

    assert event.event_type == "tool.started"
    assert event.trace_id == "trace-123"
    assert event.payload == {"tool_name": "read_file"}
