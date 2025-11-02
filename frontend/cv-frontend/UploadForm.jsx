import React, {useState} from 'react';
import axios from 'axios';

export default function UploadForm() {
  const [file, setFile] = useState(null);
  const [apiKey, setApiKey] = useState('');

  const upload = async (e) => {
    e.preventDefault();
    if(!file) return alert("Pick a PDF");
    const form = new FormData();
    form.append("file", file);
    form.append("api_key", apiKey);
    try {
      const res = await axios.post("http://127.0.0.1:8000/upload", form, {
        headers: {'Content-Type': 'multipart/form-data'}
      });
      alert("Uploaded: " + JSON.stringify(res.data));
    } catch(err) {
      alert("Upload error: " + err.response?.data?.detail || err.message);
    }
  }

  return (
    <form onSubmit={upload}>
      <input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files[0])} />
      <input type="password" placeholder="Backend API Key" value={apiKey} onChange={e=>setApiKey(e.target.value)} />
      <button type="submit">Upload CV</button>
    </form>
  );
}
