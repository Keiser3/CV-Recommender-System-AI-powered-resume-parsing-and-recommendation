import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const API_KEY = "vur47lz7iq83xd22ryo56fpuo18ox3cp"; // replace with your BACKEND_API_KEY

  const handleUpload = async () => {
    if (!file) return alert("Select a file first!");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("api_key", API_KEY);

    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    alert("Upload result: " + JSON.stringify(data));
  };

  const handleRecommend = async () => {
    const formData = new FormData();
    formData.append("query", query);
    formData.append("api_key", API_KEY);
    formData.append("top_k", 5);

    const res = await fetch("http://localhost:8000/recommend", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setResults(data.results);
  };

  return (
    <div className="App">
      <h1>CV Recommender Demo</h1>

      <h2>Upload CV</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload PDF</button>

      <h2>Search CVs</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter search query"
      />
      <button onClick={handleRecommend}>Search</button>

      <h2>Results</h2>
      {results.length === 0 ? (
        <p>No results yet</p>
      ) : (
        <ul>
          {results.map((r) => (
            <li key={r.db_id}>
              <strong>{r.filename}</strong> - Score: {r.score.toFixed(2)}
              <pre>{JSON.stringify(r.cv, null, 2)}</pre>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
