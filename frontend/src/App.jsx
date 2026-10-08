import { useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import FileTree from "./components/FileTree";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

function App() {
  const [githubUrl, setGithubUrl] = useState("");
  const [repositoryId, setRepositoryId] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [overview, setOverview] = useState(null);
  const [architecture, setArchitecture] = useState(null);
  const [repositoryView, setRepositoryView] = useState("overview");

const [highlightedLines, setHighlightedLines] = useState({
  start: null,
  end: null,
});

  const [fileQuestion, setFileQuestion] = useState("");
  const [fileAnswer, setFileAnswer] = useState("");
  const [fileSources, setFileSources] = useState([]);
  const [askingAboutFile, setAskingAboutFile] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);

  const [loading, setLoading] = useState(false);
  const [asking, setAsking] = useState(false);

  const [message, setMessage] = useState("");

  // Progress information
  const [status, setStatus] = useState("");
  const [filesProcessed, setFilesProcessed] = useState(0);
  const [chunksCreated, setChunksCreated] = useState(0);
  const [embeddingProcessed, setEmbeddingProcessed] = useState(0);
  const [totalEmbeddingBatches, setTotalEmbeddingBatches] = useState(0);

  const suggestedQuestions = [
    "What is the main architecture of this repository?",
    "Where is authentication implemented?",
    "Which files handle API routing and controllers?",
    "How does this project connect to the database?",
  ];

  const selectSuggestedQuestion = (prompt) => setQuestion(prompt);

  // =====================================================
  // Fetch Repository Overview
  // =====================================================
  
const getLanguageFromFile = (filePath) => {
  const extension = filePath
    .split(".")
    .pop()
    .toLowerCase();

  const languages = {
    java: "java",
    py: "python",
    js: "javascript",
    jsx: "jsx",
    ts: "typescript",
    tsx: "tsx",
    json: "json",
    css: "css",
    html: "xml",
    xml: "xml",
    sql: "sql",
    yml: "yaml",
    yaml: "yaml",
    sh: "bash",
    md: "markdown",
  };

  return languages[extension] || "text";
};

  const askAboutFile = async () => {
  if (
    !fileQuestion.trim() ||
    !repositoryId ||
    !selectedFile
  ) {
    return;
  }

  setAskingAboutFile(true);
  setFileAnswer("");
  setFileSources([]);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/ask-file",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository_id: repositoryId,
          file_path: selectedFile,
          question: fileQuestion,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "File question failed"
      );
    }

    setFileAnswer(data.answer);
    setFileSources(data.sources || []);
  } catch (error) {
    setFileAnswer(error.message);
  } finally {
    setAskingAboutFile(false);
  }
};
  
  const fetchFiles = async (id) => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/repositories/${id}/files`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to load repository files"
      );
    }

    setFiles(data.files || []);
  } catch (error) {
    console.error("Files error:", error);
  }
};

const openFile = async (path) => {
  try {
    setSelectedFile(path);
    setFileContent("Loading...");

    const response = await fetch(
      `http://127.0.0.1:8000/api/repositories/${repositoryId}/file?path=${encodeURIComponent(path)}`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to load file"
      );
    }

    setFileContent(data.content);
  } catch (error) {
    setFileContent(error.message);
  }
};

  const fetchOverview = async (id) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}/overview`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load repository overview"
        );
      }

      setOverview(data);
    } catch (error) {
      console.error("Overview error:", error);
    }
  };

const jumpToSource = (source) => {
  const sourceFile = source.file;

  // Open the file if it isn't already selected
  if (selectedFile !== sourceFile) {
    openFile(sourceFile);
  }

  setHighlightedLines({
    start: source.start_line,
    end: source.end_line,
  });
};

  // =====================================================
  // Fetch Repository Architecture
  // =====================================================

  const fetchArchitecture = async (id) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}/architecture`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load repository architecture"
        );
      }

      setArchitecture(data.architecture);
    } catch (error) {
      console.error("Architecture error:", error);
    }
  };

  // =====================================================
  // Check Repository Status
  // =====================================================

  const checkRepositoryStatus = async (id) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/repositories/${id}/status`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get repository status"
        );
      }

      // Update progress
      setStatus(data.status);
      setFilesProcessed(data.files_processed || 0);
      setChunksCreated(data.chunks_created || 0);

      setEmbeddingProcessed(
        data.embedding_batches_processed || 0
      );

      setTotalEmbeddingBatches(
        data.total_embedding_batches || 0
      );

      // ==============================
      // Completed
      // ==============================

      if (data.status === "COMPLETED") {
        setLoading(false);

        setMessage(
          `Repository ready! ${data.files_processed} files and ${data.chunks_created} chunks processed.`
        );

        await fetchOverview(id);
        await fetchArchitecture(id);
        await fetchFiles(id);

        return;
      }

      // ==============================
      // Failed
      // ==============================

      if (data.status === "FAILED") {
        setLoading(false);

        setMessage(
          "Repository processing failed."
        );

        return;
      }

      // ==============================
      // Still processing
      // ==============================

      setTimeout(() => {
        checkRepositoryStatus(id);
      }, 1000);

    } catch (error) {
      setLoading(false);
      setMessage(error.message);
    }
  };

  // =====================================================
  // Scan Repository
  // =====================================================

  const scanRepository = async () => {
    if (!githubUrl.trim()) return;

    setLoading(true);
    setMessage("");

    setRepositoryId(null);

    // Clear previous repository data
    setOverview(null);
    setArchitecture(null);
    setRepositoryView("overview");
    setAnswer("");
    setSources([]);

    // Reset progress
    setFilesProcessed(0);
    setChunksCreated(0);
    setEmbeddingProcessed(0);
    setTotalEmbeddingBatches(0);

    setStatus("PROCESSING");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/repositories/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            github_url: githubUrl,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Repository scanning failed"
        );
      }

      // Backend immediately gives repository ID
      const id = data.repository_id;

      setRepositoryId(id);

      setMessage(
        "Repository processing started..."
      );

      // Start checking progress
      checkRepositoryStatus(id);

    } catch (error) {
      setLoading(false);
      setMessage(error.message);
    }
  };

  // =====================================================
  // Ask Question
  // =====================================================

  const askQuestion = async () => {
    if (!question.trim() || !repositoryId) return;

    setAsking(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repository_id: repositoryId,
            question: question,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Question failed"
        );
      }

      setAnswer(data.answer);
      setSources(data.sources || []);

    } catch (error) {
      setAnswer(error.message);

    } finally {
      setAsking(false);
    }
  };

  // =====================================================
  // Progress Percentage
  // =====================================================

  const progress =
    totalEmbeddingBatches > 0
      ? Math.round(
          (embeddingProcessed /
            totalEmbeddingBatches) *
            100
        )
      : 0;

  // =====================================================
  // Render
  // =====================================================

  return (
    <div className="app">

      {/* Header */}

      <header className="header">
        <h1>CodeLense AI</h1>

        <p>
          AI-powered GitHub Repository Intelligence
        </p>
      </header>

      <main className="container">
        <div className="dashboard-grid">
          <section className="card primary-card">
            <div className="scan-card-heading">
              <div>
                <span className="step-label">STEP 01 · CONNECT YOUR CODE</span>
                <h2>Analyze a repository</h2>
                <p className="scan-description">
                  Enter a GitHub repository URL to map its structure and make the codebase ready for questions.
                </p>
              </div>
              {repositoryId && status === "COMPLETED" && (
                <span className="status-badge success">Repository ready</span>
              )}
            </div>

            <div className="input-row">
              <label className="repository-url-field">
                <span>GitHub repository URL</span>
                <input
                  type="text"
                  placeholder="https://github.com/owner/repository"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  disabled={loading}
                />
              </label>

              <button
                className={loading ? "is-loading" : ""}
                onClick={scanRepository}
                disabled={loading}
              >
                {loading ? "Processing..." : "Scan Repository"}
              </button>
            </div>

            {message && <p className="message">{message}</p>}

            {loading && (
              <div className="progress-section">
                <div className="progress-header">
                  <span>Repository processing</span>
                  <span>{progress}%</span>
                </div>

                <div className="progress-bar is-active">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>

                <div className="progress-info">
                  <p>
                    Files: <strong>{filesProcessed}</strong>
                  </p>
                  <p>
                    Chunks: <strong>{chunksCreated}</strong>
                  </p>
                  <p>
                    Embeddings: <strong>{embeddingProcessed}</strong> / <strong>{totalEmbeddingBatches}</strong>
                  </p>
                </div>

                <p className="processing-status">
                  {embeddingProcessed === 0
                    ? "Scanning repository and creating chunks..."
                    : `Creating embeddings... ${embeddingProcessed}/${totalEmbeddingBatches}`}
                </p>
              </div>
            )}
          </section>

          <section className={`card question-panel ${answer || sources.length > 0 ? "has-response" : ""}`}>
            <div className="section-heading-row">
              <h2>Ask About Your Code</h2>
            </div>

            {repositoryId && status === "COMPLETED" && (
              <div className="prompt-list">
                {suggestedQuestions.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="prompt-chip"
                    onClick={() => selectSuggestedQuestion(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}

            <textarea
              placeholder={
                status === "COMPLETED"
                  ? "Example: Where is JWT authentication implemented?"
                  : "Scan a repository first..."
              }
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!repositoryId || status !== "COMPLETED" || asking}
            />

            <button
              className={`ask-button ${asking ? "is-loading" : ""}`}
              onClick={askQuestion}
              disabled={!repositoryId || status !== "COMPLETED" || asking}
            >
              {asking ? "Thinking..." : "Ask CodeLense"}
            </button>

            {(answer || sources.length > 0) && (
              <div className="response-block">
                {answer && (
                  <div className={`answer-panel ${sources.length === 0 ? "full-width" : ""}`}>
                    <h3>Answer</h3>
                    <div className="answer">
                      <ReactMarkdown>{answer}</ReactMarkdown>
                    </div>
                  </div>
                )}

                {sources.length > 0 && (
                  <div className={`source-panel ${!answer ? "full-width" : ""}`}>
                    <h3>Sources</h3>
                    <div className="sources">
                      {sources.map((source, index) => (
                        <div
                          className="source"
                          key={index}
                          onClick={() => jumpToSource(source)}
                          style={{ cursor: "pointer" }}
                        >
                          <div className="source-file">{source.file}</div>
                          <div className="source-info">
                            Lines {source.start_line}–{source.end_line} • Chunk {source.chunk}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>

        {repositoryId && status === "COMPLETED" && (
          <nav className="repository-view-nav" aria-label="Repository views">
            <button
              type="button"
              className={`repository-view-tab ${repositoryView === "overview" ? "active" : ""}`}
              aria-pressed={repositoryView === "overview"}
              onClick={() => setRepositoryView("overview")}
            >
              Overview
            </button>
            <button
              type="button"
              className={`repository-view-tab ${repositoryView === "architecture" ? "active" : ""}`}
              aria-pressed={repositoryView === "architecture"}
              onClick={() => setRepositoryView("architecture")}
            >
              Architecture
            </button>
            <button
              type="button"
              className={`repository-view-tab ${repositoryView === "files" ? "active" : ""}`}
              aria-pressed={repositoryView === "files"}
              onClick={() => setRepositoryView("files")}
            >
              Files{files.length > 0 ? ` (${files.length})` : ""}
            </button>
          </nav>
        )}

        {repositoryView === "overview" && (
          overview ? (
          <section className="card">
            <h2>Repository Overview</h2>

            <div className="overview-grid">
              <div className="overview-item">
                <h3>Languages</h3>
                <p>{overview.languages.join(", ") || "Not detected"}</p>
              </div>

              <div className="overview-item">
                <h3>Backend</h3>
                <p>{overview.backend.join(", ") || "Not detected"}</p>
              </div>

              <div className="overview-item">
                <h3>Frontend</h3>
                <p>{overview.frontend.join(", ") || "Not detected"}</p>
              </div>

              <div className="overview-item">
                <h3>Database</h3>
                <p>{overview.database.join(", ") || "Not detected"}</p>
              </div>

              <div className="overview-item">
                <h3>AI</h3>
                <p>{overview.ai.join(", ") || "Not detected"}</p>
              </div>

              <div className="overview-item">
                <h3>Authentication</h3>
                <p>{overview.authentication.join(", ") || "Not detected"}</p>
              </div>
            </div>

            {overview.modules.length > 0 && (
              <div className="modules-section">
                <h3>Modules</h3>
                <div className="module-list">
                  {overview.modules.map((module) => (
                    <span className="module-tag" key={module}>{module}</span>
                  ))}
                </div>
              </div>
            )}
          </section>
          ) : repositoryId && status === "COMPLETED" ? (
            <section className="card repository-view-empty">
              <h2>Repository Overview</h2>
              <p>Loading repository overview…</p>
            </section>
          ) : null
        )}

        {repositoryView === "architecture" && (
          architecture ? (
          <section className="card">
            <h2>Repository Architecture</h2>

            <div className="architecture-grid">
              <div className="architecture-item">
                <h3>Controllers</h3>
                <ul>
                  {architecture.controllers.map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-item">
                <h3>Services</h3>
                <ul>
                  {architecture.services.map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-item">
                <h3>Repositories</h3>
                <ul>
                  {architecture.repositories.map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-item">
                <h3>Models</h3>
                <ul>
                  {architecture.models.map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-item">
                <h3>Security</h3>
                <ul>
                  {architecture.security.map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-item">
                <h3>Configuration</h3>
                <ul>
                  {architecture.configuration.map((file) => (
                    <li key={file}>{file}</li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
          ) : repositoryId && status === "COMPLETED" ? (
            <section className="card repository-view-empty">
              <h2>Repository Architecture</h2>
              <p>Loading repository architecture…</p>
            </section>
          ) : null
        )}

{repositoryView === "files" && (
  files.length > 0 ? (
  <section className="card">
    <h2>Repository Files</h2>

    <div className="file-explorer">
      <div className="file-tree-panel">
        <FileTree
          files={files}
          openFile={openFile}
        />
      </div>

        <div className="file-content-panel">
          {selectedFile ? (
            <>
              <div className="file-header">
                <span>{selectedFile}</span>
              </div>

              <SyntaxHighlighter
                    language={getLanguageFromFile(selectedFile)}
                    style={oneDark}
                    showLineNumbers
                    startingLineNumber={1}
                    wrapLongLines={false}
                    lineProps={(lineNumber) => {
                      const isHighlighted =
                        highlightedLines.start !== null &&
                        lineNumber >= highlightedLines.start &&
                        lineNumber <= highlightedLines.end;

                      return {
                        style: {
                          display: "block",
                          backgroundColor: isHighlighted
                            ? "rgba(255, 255, 0, 0.15)"
                            : "transparent",
                        },
                      };
                    }}
                  >
                    {fileContent}
              </SyntaxHighlighter>

              <div className="file-question-section">
                <h3>Ask About This File</h3>

                <textarea
                  placeholder="Example: How does login work in this file?"
                  value={fileQuestion}
                  onChange={(e) =>
                    setFileQuestion(e.target.value)
                  }
                  disabled={askingAboutFile}
                />

                <button
                  className="ask-button"
                  onClick={askAboutFile}
                  disabled={
                    !fileQuestion.trim() ||
                    askingAboutFile
                  }
                >
                  {askingAboutFile
                    ? "Thinking..."
                    : "Ask About This File"}
                </button>

                {fileAnswer && (
                  <div className="file-answer">
                    <h3>Answer</h3>

                    <ReactMarkdown>
                      {fileAnswer}
                    </ReactMarkdown>
                  </div>
                )}

                {fileSources.length > 0 && (
                  <div className="file-sources">
                    <h3>Sources</h3>

                    {fileSources.map((source, index) => (
                      <div
                        className="source"
                        key={index}
                        onClick={() => jumpToSource(source)}
                        style={{ cursor: "pointer" }}
>
                        <div className="source-file">
                          {source.file}
                        </div>

                        <div className="source-info">
                          Lines {source.start_line}–
                          {source.end_line}
                          {" • "}
                          Chunk {source.chunk}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="file-placeholder">
              Select a file to view its source code
            </div>
          )}
        </div>
    </div>
  </section>
) : repositoryId && status === "COMPLETED" ? (
  <section className="card repository-view-empty">
    <h2>Repository Files</h2>
    <p>Loading repository files…</p>
  </section>
) : null
)}


      </main>

    </div>
  );
}

export default App;