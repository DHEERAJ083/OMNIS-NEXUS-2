import subprocess
import json
import sys
import os
import time

SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "omnis_nexus_server.py")

def test_mcp_handshake():
    print(f"Starting server: {SERVER_SCRIPT}...")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0 # Unbuffered
    )

    # MCP Initialize Request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    
    json_input = json.dumps(init_request) + "\n"
    print(f"Sending Initialize Request: {json_input.strip()}")
    
    try:
        # Write to stdin
        process.stdin.write(json_input)
        process.stdin.flush()
        
        # Read from stdout (blocking with timeout simulation via poll or simple read)
        # We'll try to read a line.
        output = process.stdout.readline()
        
        print(f"Received Raw Output: {output.strip()}")
        
        if not output:
            stderr_out = process.stderr.read()
            print(f"No output received. STDERR:\n{stderr_out}")
            return False

        response = json.loads(output)
        
        if "result" in response and "serverInfo" in response["result"]:
            print("\n[SUCCESS] MCP Handshake Successful!")
            print(f"Server Name: {response['result']['serverInfo']['name']}")
            print(f"Protocol Version: {response['result']['protocolVersion']}")
            return True
        else:
            print("\n[FAILED] Invalid response format.")
            print(response)
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False
    finally:
        process.terminate()
        try:
            process.wait(timeout=2)
        except:
            process.kill()

if __name__ == "__main__":
    success = test_mcp_handshake()
    sys.exit(0 if success else 1)
