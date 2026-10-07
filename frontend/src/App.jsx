import { useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";

function App() {
  const [githubUrl, setGithubUrl] = useState("");
  const [repositoryId, setRepositoryId] = useState(null);

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

        {/* =================================================
            Repository Section
        ================================================= */}

        <section className="card">

          <h2>Analyze Repository</h2>

          <div className="input-row">

            <input
              type="text"
              placeholder="Enter GitHub repository URL"
              value={githubUrl}
              onChange={(e) =>
                setGithubUrl(e.target.value)
              }
              disabled={loading}
            />

            <button
              onClick={scanRepository}
              disabled={loading}
            >
              {loading
                ? "Processing..."
                : "Scan Repository"}
            </button>

          </div>


          {/* Repository message */}

          {message && (
            <p className="message">
              {message}
            </p>
          )}


          {/* Repository ID */}

          {repositoryId && (
            <p className="repository-status">
              Repository ID:{" "}
              <strong>{repositoryId}</strong>
            </p>
          )}


          {/* =================================================
              Progress
          ================================================= */}

          {loading && (
            <div className="progress-section">

              <div className="progress-header">

                <span>
                  Repository processing
                </span>

                <span>
                  {progress}%
                </span>

              </div>


              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{
                    width: `${progress}%`,
                  }}
                />

              </div>


              <div className="progress-info">

                <p>
                  Files:{" "}
                  <strong>
                    {filesProcessed}
                  </strong>
                </p>

                <p>
                  Chunks:{" "}
                  <strong>
                    {chunksCreated}
                  </strong>
                </p>

                <p>
                  Embeddings:{" "}
                  <strong>
                    {embeddingProcessed}
                  </strong>
                  {" / "}
                  <strong>
                    {totalEmbeddingBatches}
                  </strong>
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


        {/* =================================================
            Question Section
        ================================================= */}

        <section className="card">

          <h2>Ask About Your Code</h2>

          <textarea
            placeholder={
              status === "COMPLETED"
                ? "Example: Where is JWT authentication implemented?"
                : "Scan a repository first..."
            }
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            disabled={
              !repositoryId ||
              status !== "COMPLETED" ||
              asking
            }
          />


          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={
              !repositoryId ||
              status !== "COMPLETED" ||
              asking
            }
          >
            {asking
              ? "Thinking..."
              : "Ask CodeLense"}
          </button>

        </section>


        {/* =================================================
            Answer Section
        ================================================= */}

        {answer && (
          <section className="card">

            <h2>Answer</h2>

            <div className="answer">

              <ReactMarkdown>
                {answer}
              </ReactMarkdown>

            </div>

          </section>
        )}


        {/* =================================================
            Sources Section
        ================================================= */}

        {sources.length > 0 && (
          <section className="card">

            <h2>Sources</h2>

            <div className="sources">

              {sources.map(
                (source, index) => (

                  <div
                    className="source"
                    key={index}
                  >

                    <div className="source-file">
                      {source.file}
                    </div>

                    <div className="source-info">

                      Lines{" "}
                      {source.start_line}
                      {"–"}
                      {source.end_line}

                      {" • "}

                      Chunk{" "}
                      {source.chunk}

                    </div>

                  </div>

                )
              )}

            </div>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;