"""
Mono Memory MCP Server — Test Script

Usage: cd mono-memory-mcp && uv run python test_server.py
"""

import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    uv_path = shutil.which("uv")
    if uv_path is None:
        raise RuntimeError("uv is not installed or not found in PATH")

    project_dir = str(Path(__file__).parent)

    # Use a temporary directory for the database to isolate tests
    with tempfile.TemporaryDirectory() as tmp_dir:
        env = {**os.environ, "MONO_MEMORY_DB_DIR": tmp_dir}

        server_params = StdioServerParameters(
            command=uv_path,
            args=["--directory", project_dir, "run", "python", "server.py", "--stdio"],
            env=env,
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 1. Verify tool list
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                print(f"[OK] Registered tools: {tool_names}")
                assert set(tool_names) == {
                    "memory_save", "memory_get", "memory_search",
                    "memory_timeline", "memory_init", "memory_context",
                }

                # 2. Test memory_save
                result = await session.call_tool("memory_save", {
                    "author": "test",
                    "project": "test-project",
                    "content": "Test observation: confirmed code generation pattern",
                    "tags": "test,pattern",
                })
                save_data = json.loads(result.content[0].text)
                obs_id = save_data["id"]
                print(f"[OK] memory_save: id={obs_id}")

                # 3. Test memory_get
                result = await session.call_tool("memory_get", {"id": obs_id})
                get_data = json.loads(result.content[0].text)
                assert get_data["author"] == "test"
                assert get_data["project"] == "test-project"
                print(f"[OK] memory_get: author={get_data['author']}, project={get_data['project']}")

                # 4. Test memory_search
                result = await session.call_tool("memory_search", {
                    "query": "pattern",
                    "project": "test-project",
                })
                search_data = json.loads(result.content[0].text)
                assert search_data["count"] >= 1
                print(f"[OK] memory_search: {search_data['count']} result(s) found")

                # 5. Test memory_timeline
                result = await session.call_tool("memory_timeline", {
                    "project": "test-project",
                    "limit": 10,
                })
                timeline_data = json.loads(result.content[0].text)
                assert timeline_data["count"] >= 1
                print(f"[OK] memory_timeline: {timeline_data['count']} entry(ies) retrieved")

                # 6. Test memory_init
                result = await session.call_tool("memory_init", {
                    "project": "test-project",
                    "section": "overview",
                    "content": "A test project for verifying the memory server",
                    "author": "test",
                })
                init_data = json.loads(result.content[0].text)
                assert init_data["status"] == "updated"
                print(f"[OK] memory_init: section={init_data['section']}")

                # 7. Test memory_context
                result = await session.call_tool("memory_context", {
                    "project": "test-project",
                })
                ctx_data = json.loads(result.content[0].text)
                assert len(ctx_data["sections"]) >= 1
                print(f"[OK] memory_context: {len(ctx_data['sections'])} section(s)")

                # 8. Test memory_get with nonexistent ID
                result = await session.call_tool("memory_get", {"id": "nonexistent-id"})
                not_found = json.loads(result.content[0].text)
                assert not_found.get("error") == "not_found"
                print("[OK] memory_get (not found): error handling works")

                print("\n=== All tests passed! ===")


if __name__ == "__main__":
    asyncio.run(main())
