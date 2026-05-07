import React, { useState, useEffect } from "react";
import "./App.scss";

interface HelloResponse {
  message: string;
}

const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || "";

function App() {
  const [data, setData] = useState<HelloResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${apiBaseUrl}/hello/?name=Docker`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const json: HelloResponse = await response.json();
        setData(json);
      } catch (err: any) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error?.message}</div>; // Optional chaining for error message
  }

  if (data) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Backend Connection</h1>
          <p>{data.message}</p>
          <p>API Base URL: {apiBaseUrl || "(CRA proxy -> localhost:8001)"}</p>
        </header>
      </div>
    );
  }

  return null;
}

export default App;
