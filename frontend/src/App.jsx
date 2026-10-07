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
  const [message, setMessage] = useState("");

  const scanRepository = async () => {
    if (!githubUrl.trim()) return;

    setLoading(true);
    setMessage("");
    setRepositoryId(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/repositories/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          github_url: githubUrl,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Repository scanning failed");
      }

      setRepositoryId(data.repository_id);

      setMessage(
        `Repository scanned successfully. ${data.files_processed} files and ${data.chunks_created} chunks created.`
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim() || !repositoryId) return;

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository_id: repositoryId,
          question: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Question failed");
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setAnswer(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>CodeLense AI</h1>
        <p>AI-powered GitHub Repository Intelligence</p>
      </header>

      <main className="container">

        {/* Repository Section */}
        <section className="card">
          <h2>Analyze Repository</h2>

          <div className="input-row">
            <input
              type="text"
              placeholder="Enter GitHub repository URL"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
            />

            <button onClick={scanRepository} disabled={loading}>
              {loading ? "Scanning..." : "Scan Repository"}
            </button>
          </div>

          {message && (
            <p className="message">
              {message}
            </p>
          )}

          {repositoryId && (
            <p className="repository-status">
              Repository ID: <strong>{repositoryId}</strong>
            </p>
          )}
        </section>

        {/* Question Section */}
        <section className="card">
          <h2>Ask About Your Code</h2>

          <textarea
            placeholder={
              repositoryId
                ? "Example: Where is JWT authentication implemented?"
                : "Scan a repository first..."
            }
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!repositoryId}
          />

          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={!repositoryId || loading}
          >
            {loading ? "Thinking..." : "Ask CodeLense"}
          </button>
        </section>

        {/* Answer Section */}
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

        {/* Sources Section */}
        {sources.length > 0 && (
          <section className="card">
            <h2>Sources</h2>

            <div className="sources">
              {sources.map((source, index) => (
                <div className="source" key={index}>
                  <div className="source-file">
                    {source.file}
                  </div>

                  <div className="source-info">
                    Lines {source.start_line}–{source.end_line}
                    {" • "}
                    Chunk {source.chunk}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

      </main>
    </div>
  );
}

export default App;