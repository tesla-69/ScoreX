import React, { useState } from 'react';

export default function ResumeJDUploader() {
  const [resumes, setResumes] = useState([]);
  const [jdFile, setJdFile] = useState(null);

  const handleResumesChange = (e) => {
    const files = Array.from(e.target.files);
    setResumes(files);
  };

  const handleJDChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.csv')) {
      setJdFile(file);
    } else {
      alert('Please upload a valid .csv file for JD');
      e.target.value = '';
      setJdFile(null);
    }
  };

  const isFormValid = resumes.length >= 3 && jdFile;

  const handleSubmit = () => {
    if (!isFormValid) return;
    // Submission logic here
    console.log('Submitting...', { resumes, jdFile });
    alert('Submitted!');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-xl space-y-6">
        <h2 className="text-2xl font-bold text-gray-800">Upload Resumes & Job Description</h2>

        <div>
          <label className="block text-gray-700 font-medium mb-1">Upload Resumes (min 3):</label>
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            multiple
            onChange={handleResumesChange}
            className="w-full border rounded p-2"
          />
          <p className="text-sm text-gray-500 mt-1">{resumes.length} file(s) selected</p>
        </div>

        <div>
          <label className="block text-gray-700 font-medium mb-1">Upload JD (.csv):</label>
          <input
            type="file"
            accept=".csv"
            onChange={handleJDChange}
            className="w-full border rounded p-2"
          />
          {jdFile && <p className="text-sm text-gray-500 mt-1">Selected: {jdFile.name}</p>}
        </div>

        <button
          disabled={!isFormValid}
          onClick={handleSubmit}
          className={`w-full py-2 px-4 rounded-xl text-white font-semibold transition ${
            isFormValid ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          Submit
        </button>
      </div>
    </div>
  );
}
