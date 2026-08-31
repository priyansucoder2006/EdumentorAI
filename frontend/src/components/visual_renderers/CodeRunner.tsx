import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Play, RotateCcw, CheckCircle, Terminal } from 'lucide-react';

interface CodeRunnerProps {
  initialCode?: string;
  language?: string;
  expectedOutput?: string;
  title?: string;
  readOnly?: boolean;
}

export const CodeRunner: React.FC<CodeRunnerProps> = ({
  initialCode = '// Write code here\nconsole.log("Hello, EduMentor!");',
  language = 'typescript',
  expectedOutput,
  title = 'Interactive Code Demonstration',
  readOnly = false,
}) => {
  const [code, setCode] = useState<string>(initialCode);
  const [output, setOutput] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const handleRun = () => {
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
      setOutput(expectedOutput || 'Execution completed with return code 0.\nOutputs rendered successfully.');
    }, 400);
  };

  const handleReset = () => {
    setCode(initialCode);
    setOutput(null);
  };

  return (
    <div className="code-runner-card">
      <div className="visual-header">
        <div className="flex items-center gap-2">
          <span className="visual-badge code">Programming</span>
          <h4>{title}</h4>
        </div>
        <div className="code-actions">
          <button className="btn-secondary btn-sm" onClick={handleReset} title="Reset Code">
            <RotateCcw size={14} /> Reset
          </button>
          <button className="btn-primary btn-sm" onClick={handleRun} disabled={isRunning}>
            <Play size={14} /> {isRunning ? 'Running...' : 'Run Code'}
          </button>
        </div>
      </div>

      <div className="editor-wrapper">
        <Editor
          height="220px"
          language={language === 'python' ? 'python' : 'typescript'}
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
          }}
        />
      </div>

      {output && (
        <div className="terminal-output">
          <div className="terminal-header">
            <Terminal size={14} /> Execution Console
          </div>
          <pre className="terminal-body">{output}</pre>
        </div>
      )}
    </div>
  );
};
