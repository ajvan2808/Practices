# Documenting Your Code With Assertions
def get_response(server, ports=(443, 80)):
    # port arg expected non-empty tuple
    assert len(ports) > 0, f"ports expected non-empty tuple, got {ports}."
    for port in ports:
        if server.connect(port):
            return server.get()
    return None
