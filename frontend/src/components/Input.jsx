import React, { useState } from "react";
import { uploadFiles } from "../services/uploadService";

export default function ResumeJDUploader() {
    const [resumes, setResumes] = useState([]);
    const [jdFile, setJdFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleResumesChange = (e) => {
        const files = Array.from(e.target.files);
        setResumes(files);
        setError(null);
        setSuccess(false);
    };

    const handleJDChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setJdFile(file);
            setError(null);
            setSuccess(false);
        }
    };

    const isFormValid = resumes.length > 0 && jdFile;

    const handleSubmit = async () => {
        if (!isFormValid) return;

        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            const result = await uploadFiles(resumes, jdFile);
            console.log('Upload successful:', result);
            setSuccess(true);
            // Clear form after successful upload
            setResumes([]);
            setJdFile(null);
            // Reset file inputs
            document.getElementById('resumeInput').value = '';
            document.getElementById('jdInput').value = '';
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
            <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-xl space-y-6">
                <h2 className="text-2xl font-bold text-gray-800">
                    Upload Resumes & Job Description
                </h2>

                <div>
                    <label className="block text-gray-700 font-medium mb-1">
                        Upload Resumes:
                    </label>
                    <input
                        id="resumeInput"
                        type="file"
                        accept=".pdf,.doc,.docx"
                        multiple
                        onChange={handleResumesChange}
                        className="w-full border rounded p-2"
                    />
                    <p className="text-sm text-gray-500 mt-1">
                        {resumes.length} file(s) selected
                    </p>
                </div>

                <div>
                    <label className="block text-gray-700 font-medium mb-1">
                        Upload Job Description:
                    </label>
                    <input
                        id="jdInput"
                        type="file"
                        accept=".pdf,.doc,.docx,.csv"
                        onChange={handleJDChange}
                        className="w-full border rounded p-2"
                    />
                    {jdFile && (
                        <p className="text-sm text-gray-500 mt-1">
                            Selected: {jdFile.name}
                        </p>
                    )}
                </div>

                {error && (
                    <div className="text-red-500 text-sm p-3 bg-red-50 rounded">
                        Error: {error}
                    </div>
                )}

                {success && (
                    <div className="text-green-500 text-sm p-3 bg-green-50 rounded">
                        Files uploaded successfully!
                    </div>
                )}

                <button
                    disabled={!isFormValid || loading}
                    onClick={handleSubmit}
                    className={`w-full py-2 px-4 rounded-xl text-white font-semibold transition ${
                        isFormValid && !loading
                            ? "bg-blue-600 hover:bg-blue-700"
                            : "bg-gray-400 cursor-not-allowed"
                    }`}
                >
                    {loading ? "Uploading..." : "Submit"}
                </button>
            </div>
        </div>
    );
}