import pytest
from unittest.mock import patch, AsyncMock
from app.services.code_execution.code_service import CodeExecutionService
from app.services.code_execution.language_resolver import LanguageResolver
from app.services.code_execution.judge0_provider import Judge0Provider
from app.schemas.code_execution import CodeExecutionResult, LanguageItem


@pytest.mark.asyncio
async def test_language_resolver_aliases():
    resolver = LanguageResolver()
    
    # Test Python aliases
    lid, name = resolver.resolve_language("python")
    assert name == "python"
    lid3, name3 = resolver.resolve_language("python3")
    assert name3 == "python"

    # Test C++ aliases
    _, name_cpp = resolver.resolve_language("c++")
    assert name_cpp == "cpp"
    _, name_cpp2 = resolver.resolve_language("c plus plus")
    assert name_cpp2 == "cpp"

    # Test JavaScript / TypeScript
    _, name_js = resolver.resolve_language("javascript")
    assert name_js == "javascript"
    _, name_ts = resolver.resolve_language("ts")
    assert name_ts == "typescript"

    # Test C# & Go & Rust & Ruby
    _, name_cs = resolver.resolve_language("c#")
    assert name_cs == "csharp"
    _, name_go = resolver.resolve_language("golang")
    assert name_go == "go"
    _, name_rust = resolver.resolve_language("rust")
    assert name_rust == "rust"
    _, name_ruby = resolver.resolve_language("ruby")
    assert name_ruby == "ruby"


def test_language_resolver_invalid_and_rails():
    resolver = LanguageResolver()
    
    # Rails disambiguation
    with pytest.raises(ValueError) as exc:
        resolver.resolve_language("Ruby on Rails")
    assert "Ruby on Rails is a full-stack web application framework" in str(exc.value)

    # Unsupported language
    with pytest.raises(ValueError) as exc2:
        resolver.resolve_language("brainfuck_nonexistent")
    assert "Unsupported language" in str(exc2.value)


@pytest.mark.asyncio
async def test_python_code_execution_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=True,
        language="python",
        status="Accepted",
        stdout="4\n",
        stderr="",
        compile_output="",
        execution_time="0.02s",
        memory="7820 KB",
        status_id=3
    )
    
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("python", "print(2 + 2)")
        
        assert res.success is True
        assert res.stdout.strip() == "4"
        assert res.status == "Accepted"


@pytest.mark.asyncio
async def test_c_code_execution_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=True,
        language="c",
        status="Accepted",
        stdout="Hello C\n",
        stderr="",
        compile_output="",
        execution_time="0.01s",
        memory="2048 KB",
        status_id=3
    )
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("c", '#include <stdio.h>\nint main(){printf("Hello C\\n");return 0;}')
        assert res.success is True
        assert "Hello C" in res.stdout


@pytest.mark.asyncio
async def test_java_code_execution_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=True,
        language="java",
        status="Accepted",
        stdout="Hello Java\n",
        stderr="",
        compile_output="",
        execution_time="0.08s",
        memory="32000 KB",
        status_id=3
    )
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("java", 'public class Main { public static void main(String[] args){System.out.println("Hello Java");} }')
        assert res.success is True
        assert "Hello Java" in res.stdout


@pytest.mark.asyncio
async def test_javascript_code_execution_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=True,
        language="javascript",
        status="Accepted",
        stdout="Hello Node\n",
        stderr="",
        compile_output="",
        execution_time="0.03s",
        memory="28000 KB",
        status_id=3
    )
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("javascript", 'console.log("Hello Node");')
        assert res.success is True
        assert "Hello Node" in res.stdout


@pytest.mark.asyncio
async def test_ruby_code_execution_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=True,
        language="ruby",
        status="Accepted",
        stdout="Hello Ruby\n",
        stderr="",
        compile_output="",
        execution_time="0.02s",
        memory="12000 KB",
        status_id=3
    )
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("ruby", 'puts "Hello Ruby"')
        assert res.success is True
        assert "Hello Ruby" in res.stdout



@pytest.mark.asyncio
async def test_cpp_compilation_error_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=False,
        language="cpp",
        status="Compilation Error",
        stdout="",
        stderr="",
        compile_output="main.cpp: In function 'int main()':\nmain.cpp:2:5: error: 'cout' was not declared",
        execution_time=None,
        memory=None,
        error="main.cpp:2:5: error: 'cout' was not declared",
        status_id=6
    )
    
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("c++", "int main() { cout << 4; }")
        
        assert res.success is False
        assert res.status == "Compilation Error"
        assert "not declared" in res.compile_output


@pytest.mark.asyncio
async def test_runtime_error_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=False,
        language="python",
        status="Runtime Error (NZEC)",
        stdout="",
        stderr="ZeroDivisionError: division by zero",
        compile_output="",
        execution_time="0.01s",
        memory="6500 KB",
        error="ZeroDivisionError: division by zero",
        status_id=11
    )
    
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("python", "print(10 / 0)")
        
        assert res.success is False
        assert "Runtime Error" in res.status
        assert "ZeroDivisionError" in res.stderr


@pytest.mark.asyncio
async def test_stdin_handling_mocked():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=True,
        language="python",
        status="Accepted",
        stdout="Doubled: 20\n",
        stderr="",
        compile_output="",
        execution_time="0.02s",
        memory="7800 KB",
        status_id=3
    )
    
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_result
        res = await service.execute_code("python", "n = int(input())\nprint(f'Doubled: {n*2}')", stdin="10")
        
        assert res.success is True
        assert "Doubled: 20" in res.stdout
        mock_exec.assert_called_once()
        assert mock_exec.call_args[1]["stdin"] == "10"


@pytest.mark.asyncio
async def test_judge0_unavailable_fallback():
    service = CodeExecutionService()
    mock_result = CodeExecutionResult(
        success=False,
        language="python",
        status="Service Unavailable",
        error="Code execution service is temporarily unavailable. Please verify the self-hosted Judge0 instance is running."
    )
    
    with patch.object(service.provider, "execute_code", new_callable=AsyncMock) as mock_exec, \
         patch.object(service, "_simulate_pedagogical_execution", new_callable=AsyncMock) as mock_sim:
        
        # 1. When simulation succeeds
        mock_exec.return_value = mock_result
        mock_sim.return_value = CodeExecutionResult(
            success=True,
            language="python",
            status="Accepted (AI Sandbox)",
            stdout="hello\n"
        )
        res = await service.execute_code("python", "print('hello')")
        assert res.success is True
        assert "AI Sandbox" in res.status

        # 2. When simulation is not available / fails
        mock_sim.return_value = None
        res_fail = await service.execute_code("python", "print('hello')")
        assert res_fail.success is False
        assert "temporarily unavailable" in res_fail.error



def test_code_execution_api_endpoint(client, auth_headers):
    mock_res = CodeExecutionResult(
        success=True,
        language="python",
        status="Accepted",
        stdout="Hello World\n",
        stderr="",
        compile_output="",
        execution_time="0.02s",
        memory="7000 KB"
    )
    with patch.object(CodeExecutionService, "execute_code", new_callable=AsyncMock) as mock_srv:
        mock_srv.return_value = mock_res
        
        response = client.post(
            "/api/code/execute",
            headers=auth_headers,
            json={
                "language": "python",
                "sourceCode": "print('Hello World')",
                "stdin": ""
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"]["stdout"] == "Hello World\n"


def test_code_health_endpoint(client):
    response = client.get("/api/code/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "languages_count" in data
