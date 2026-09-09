import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import {
  Play,
  RotateCcw,
  Terminal,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Cpu,
  ChevronDown,
  ChevronUp,
  FileCode,
  Sparkles
} from 'lucide-react';
import { codeService } from '../../services/codeService';
import { CodeExecutionResult } from '../../types';

interface CodeRunnerProps {
  initialCode?: string;
  language?: string;
  expectedOutput?: string;
  title?: string;
  readOnly?: boolean;
}

const SUPPORTED_LANGUAGES = [
  { id: 'python', name: 'Python 3', monacoLang: 'python', defaultSnippet: 'print("Hello from EduMentor AI!")\n\n# Calculate factorial\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)\n\nprint("Factorial of 5:", factorial(5))' },
  { id: 'javascript', name: 'JavaScript (Node.js)', monacoLang: 'javascript', defaultSnippet: 'console.log("Hello from EduMentor AI!");\n\nconst nums = [1, 2, 3, 4, 5];\nconst sum = nums.reduce((a, b) => a + b, 0);\nconsole.log("Sum:", sum);' },
  { id: 'typescript', name: 'TypeScript', monacoLang: 'typescript', defaultSnippet: 'const greeting: string = "Hello from EduMentor AI!";\nconsole.log(greeting);\n\ninterface User {\n  id: number;\n  name: string;\n}\n\nconst user: User = { id: 1, name: "Learner" };\nconsole.log(`User: ${user.name} (#${user.id})`);' },
  { id: 'cpp', name: 'C++ (GCC)', monacoLang: 'cpp', defaultSnippet: '#include <iostream>\n\nint main() {\n    std::cout << "Hello from EduMentor AI C++!" << std::endl;\n    int a = 10, b = 20;\n    std::cout << "Sum: " << (a + b) << std::endl;\n    return 0;\n}' },
  { id: 'c', name: 'C (GCC)', monacoLang: 'c', defaultSnippet: '#include <stdio.h>\n\nint main() {\n    printf("Hello from EduMentor AI C!\\n");\n    return 0;\n}' },
  { id: 'java', name: 'Java (OpenJDK)', monacoLang: 'java', defaultSnippet: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from EduMentor AI Java!");\n    }\n}' },
  { id: 'csharp', name: 'C# (Mono/.NET)', monacoLang: 'csharp', defaultSnippet: 'using System;\n\npublic class Program {\n    public static void Main() {\n        Console.WriteLine("Hello from EduMentor AI C#!");\n    }\n}' },
  { id: 'go', name: 'Go (Golang)', monacoLang: 'go', defaultSnippet: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello from EduMentor AI Go!")\n}' },
  { id: 'rust', name: 'Rust', monacoLang: 'rust', defaultSnippet: 'fn main() {\n    println!("Hello from EduMentor AI Rust!");\n}' },
  { id: 'ruby', name: 'Ruby', monacoLang: 'ruby', defaultSnippet: 'puts "Hello from EduMentor AI Ruby!"\nnums = [1, 2, 3, 4, 5]\nputs "Sum: #{nums.sum}"' },
];

export const CodeRunner: React.FC<CodeRunnerProps> = ({
  initialCode,
  language = 'python',
  expectedOutput,
  title = 'Interactive Multi-Language Code Runner',
  readOnly = false,
}) => {
  // Normalize initial language
  const findLangObj = (langName: string) => {
    const l = langName.toLowerCase().trim();
    if (l === 'c++' || l === 'c plus plus') return SUPPORTED_LANGUAGES.find((item) => item.id === 'cpp');
    if (l === 'c#' || l === 'c sharp') return SUPPORTED_LANGUAGES.find((item) => item.id === 'csharp');
    if (l === 'js' || l === 'node') return SUPPORTED_LANGUAGES.find((item) => item.id === 'javascript');
    if (l === 'ts') return SUPPORTED_LANGUAGES.find((item) => item.id === 'typescript');
    if (l === 'py') return SUPPORTED_LANGUAGES.find((item) => item.id === 'python');
    if (l === 'golang') return SUPPORTED_LANGUAGES.find((item) => item.id === 'go');
    return SUPPORTED_LANGUAGES.find((item) => item.id === l) || SUPPORTED_LANGUAGES[0];
  };

  const initialLangObj = findLangObj(language);
  const [selectedLang, setSelectedLang] = useState<string>(initialLangObj?.id || 'python');
  const [code, setCode] = useState<string>(initialCode || initialLangObj?.defaultSnippet || '');
  const [stdin, setStdin] = useState<string>('');
  const [showStdin, setShowStdin] = useState<boolean>(false);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [executionResult, setExecutionResult] = useState<CodeExecutionResult | null>(
    expectedOutput
      ? {
          success: true,
          language: selectedLang,
          status: 'Accepted',
          stdout: expectedOutput,
          stderr: '',
          compile_output: '',
          execution_time: '0.01s',
          memory: '4096 KB',
        }
      : null
  );

  const currentLangObj = SUPPORTED_LANGUAGES.find((l) => l.id === selectedLang) || SUPPORTED_LANGUAGES[0];

  const handleLanguageChange = (newLangId: string) => {
    setSelectedLang(newLangId);
    const target = SUPPORTED_LANGUAGES.find((l) => l.id === newLangId);
    if (target && (!code || code === currentLangObj.defaultSnippet)) {
      setCode(target.defaultSnippet);
    }
  };

  const handleRun = async () => {
    setIsRunning(true);
    try {
      const response = await codeService.executeCode(selectedLang, code, stdin);
      setExecutionResult(response.result);
    } catch (err: any) {
      setExecutionResult({
        success: false,
        language: selectedLang,
        status: 'Execution Failed',
        stdout: '',
        stderr: err.message || 'Connection error with execution service',
        compile_output: '',
        error: err.message || 'Unable to execute code.',
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    setCode(initialCode || currentLangObj.defaultSnippet);
    setStdin('');
    setExecutionResult(null);
  };

  return (
    <div className="code-runner-card bg-slate-900 border border-slate-700/80 rounded-xl overflow-hidden shadow-xl">
      {/* Header bar */}
      <div className="visual-header p-3 sm:p-4 bg-slate-800/80 border-b border-slate-700 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="visual-badge code flex items-center gap-1 bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded-full text-xs font-semibold">
            <FileCode size={13} /> Self-Hosted Judge0
          </span>
          <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
        </div>

        <div className="code-actions flex items-center gap-2">
          {/* Language Selector */}
          <select
            value={selectedLang}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="bg-slate-900 text-slate-200 border border-slate-700 rounded-lg text-xs px-2.5 py-1.5 focus:outline-none focus:border-blue-500 font-medium"
            title="Select Language"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </select>

          {/* Stdin Toggle */}
          <button
            className={`btn-secondary btn-sm flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg border transition-colors ${
              showStdin ? 'bg-slate-700 text-white border-slate-600' : 'bg-slate-800 text-slate-300 border-slate-700'
            }`}
            onClick={() => setShowStdin(!showStdin)}
            title="Toggle Standard Input (stdin)"
          >
            <span>stdin</span>
            {showStdin ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>

          {/* Reset button */}
          <button
            className="btn-secondary btn-sm flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            onClick={handleReset}
            title="Reset Code"
          >
            <RotateCcw size={13} />
            <span className="hidden sm:inline">Reset</span>
          </button>

          {/* Run button */}
          <button
            className="btn-primary btn-sm flex items-center gap-1.5 text-xs px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-md transition-all disabled:opacity-50"
            onClick={handleRun}
            disabled={isRunning}
          >
            {isRunning ? (
              <>
                <span className="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent" />
                <span>Running...</span>
              </>
            ) : (
              <>
                <Play size={13} fill="currentColor" />
                <span>Run Code</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Optional Stdin Panel */}
      {showStdin && (
        <div className="p-3 bg-slate-950 border-b border-slate-800">
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            Standard Input (stdin):
          </label>
          <textarea
            value={stdin}
            onChange={(e) => setStdin(e.target.value)}
            placeholder="Type input data here (e.g. 10 or test values)..."
            rows={2}
            className="w-full bg-slate-900 text-slate-200 text-xs font-mono p-2 rounded border border-slate-700 focus:outline-none focus:border-blue-500 resize-y"
          />
        </div>
      )}

      {/* Monaco Code Editor */}
      <div className="editor-wrapper border-b border-slate-800">
        <Editor
          height="240px"
          language={currentLangObj.monacoLang}
          value={code}
          theme="vs-dark"
          onChange={(val) => setCode(val || '')}
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          }}
        />
      </div>

      {/* Execution Results Terminal */}
      {executionResult && (
        <div className="terminal-output bg-slate-950 p-3 sm:p-4">
          {/* Header with status badges and metrics */}
          <div className="terminal-header flex flex-wrap items-center justify-between gap-2 pb-2 mb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Terminal size={14} className="text-slate-400" />
              <span className="text-xs font-semibold text-slate-300">Execution Console</span>
              {executionResult.success ? (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  <CheckCircle size={11} /> {executionResult.status}
                </span>
              ) : (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  <XCircle size={11} /> {executionResult.status}
                </span>
              )}
            </div>

            {/* Performance stats */}
            <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
              {executionResult.execution_time && (
                <div className="flex items-center gap-1" title="Execution Time">
                  <Clock size={12} className="text-cyan-400" />
                  <span>{executionResult.execution_time}</span>
                </div>
              )}
              {executionResult.memory && (
                <div className="flex items-center gap-1" title="Memory Used">
                  <Cpu size={12} className="text-purple-400" />
                  <span>{executionResult.memory}</span>
                </div>
              )}
            </div>
          </div>

          {/* Docker Tip if AI Sandbox was used */}
          {executionResult.status.includes('AI Sandbox') && (
            <div className="mb-2.5 px-3 py-1.5 rounded-lg bg-blue-950/40 border border-blue-800/40 text-[11px] text-blue-300 flex items-center justify-between">
              <span>⚡ Executed via AI Sandbox (Judge0 Docker is offline).</span>
              <code className="bg-slate-900 px-1.5 py-0.5 rounded text-[10px] text-cyan-300 font-mono">
                docker compose -f docker-compose.judge0.yml up -d
              </code>
            </div>
          )}

          {/* Compiler Error / Diagnostics Panel */}
          {executionResult.compile_output && (
            <div className="mb-3 p-3 rounded-lg bg-rose-950/40 border border-rose-500/40 text-rose-200 text-xs font-mono">
              <div className="flex items-center gap-1.5 font-bold text-rose-400 mb-1">
                <AlertTriangle size={13} /> Compiler Output:
              </div>
              <pre className="whitespace-pre-wrap overflow-x-auto text-[12px]">{executionResult.compile_output}</pre>
            </div>
          )}

          {/* Runtime Standard Error */}
          {executionResult.stderr && (
            <div className="mb-3 p-3 rounded-lg bg-amber-950/40 border border-amber-500/40 text-amber-200 text-xs font-mono">
              <div className="flex items-center gap-1.5 font-bold text-amber-400 mb-1">
                <AlertTriangle size={13} /> Standard Error (stderr):
              </div>
              <pre className="whitespace-pre-wrap overflow-x-auto text-[12px]">{executionResult.stderr}</pre>
            </div>
          )}

          {/* Standard Output Console */}
          {executionResult.stdout ? (
            <div className="bg-slate-900/90 rounded-lg p-3 border border-slate-800">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                Standard Output (stdout):
              </div>
              <pre className="text-emerald-400 font-mono text-xs whitespace-pre-wrap overflow-x-auto leading-relaxed">
                {executionResult.stdout}
              </pre>
            </div>
          ) : !executionResult.compile_output && !executionResult.stderr ? (
            <div className="text-xs text-slate-500 italic">Program executed with no standard output.</div>
          ) : null}

          {/* General Error Message */}
          {executionResult.error && !executionResult.compile_output && !executionResult.stderr && (
            <div className="p-2.5 rounded bg-rose-950/30 text-rose-300 text-xs border border-rose-800/50">
              <strong>Error:</strong> {executionResult.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
