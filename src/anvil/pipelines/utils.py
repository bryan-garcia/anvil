def _pipeline_heads(pipeline) -> list[str]:
    """
    Return component names that have no inbound edges (i.e., “heads” you feed via run(data=...)).
    Strategy: use pipeline.to_dict() and analyze connections.
    """
    try:
        pdata = pipeline.to_dict()  # Haystack 2.x exposes this
    except Exception:
        # Fallback: best-effort—no heads available
        return []
    components = set(pdata.get("components", {}).keys())
    receivers = set()
    for c in pdata.get("connections", []):
        recv = c.get("receiver", "")
        # format "component.input_socket"
        if "." in recv:
            recv_comp = recv.split(".", 1)[0]
        else:
            recv_comp = recv
        receivers.add(recv_comp)
    heads = sorted(components - receivers)
    return heads
