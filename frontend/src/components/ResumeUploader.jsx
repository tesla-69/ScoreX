import React, { useState, useEffect } from 'react';
import { uploadResume, uploadJobDescription, getProcessingStatus, getMatchResults, getGraph, getWordcloud, getTopMatches } from '../services/api';
import './ResumeUploader.css';

const ResumeUploader = () => {
    const [resumes, setResumes] = useState([]);
    const [jobDescription, setJobDescription] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [results, setResults] = useState([]); // This will hold top 3 results with URLs
    const [error, setError] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [allProcessedResumes, setAllProcessedResumes] = useState([]);
    const [shortlistedResumeNames, setShortlistedResumeNames] = useState([]);
    const [nonShortlistedResumeNames, setNonShortlistedResumeNames] = useState([]);

    useEffect(() => {
        const checkProcessingStatus = async () => {
            try {
                const status = await getProcessingStatus();
                setProcessing(status.is_processing);
                
                if (!status.is_processing && status.has_job_description) {
                    // Fetch results for top 3 matches
                    const fetchedResults = [];
                    const top3Names = [];
                    for (let i = 1; i <= 3; i++) {
                        try {
                            const result = await getMatchResults(i);
                            const graphBlob = await getGraph(i);
                            const wordcloudBlob = await getWordcloud(i);
                            
                            fetchedResults.push({
                                ...result,
                                graphUrl: URL.createObjectURL(graphBlob),
                                wordcloudUrl: URL.createObjectURL(wordcloudBlob)
                            });

                            // Ensure result.results is an array and has at least one element,
                            // and that the first element has a 'Candidate' property.
                            if (result.results && Array.isArray(result.results) && result.results.length > 0 && result.results[0].Candidate) {
                                top3Names.push(result.results[0].Candidate);
                            } else {
                                console.warn(`Candidate name not found or results empty for match ${i}. Result structure:`, result);
                                // If no candidate name, still push a placeholder to maintain array length for display
                                top3Names.push(`Match ${i} (No Candidate Found)`);
                            }

                        } catch (resultErr) {
                            console.warn(`Failed to fetch visual results for match ${i}:`, resultErr.message);
                            // Push a placeholder for the name to maintain list length
                            top3Names.push(`Match ${i} (Error Loading)`);
                        }
                    }
                    setResults(fetchedResults);
                    setShortlistedResumeNames(top3Names);

                    // Fetch all processed resume names
                    try {
                        const allCandidates = await getTopMatches();
                        setAllProcessedResumes(allCandidates.candidates || []);
                        const nonShortlisted = (allCandidates.candidates || []).filter(name => !top3Names.includes(name));
                        setNonShortlistedResumeNames(nonShortlisted);
                    } catch (topMatchesErr) {
                        console.error("Failed to fetch all processed resume names:", topMatchesErr.message);
                        setError("Failed to load all processed resume names.");
                    }

                } else if (!status.is_processing && !status.has_job_description) {
                    // Reset results if no JD and not processing
                    setResults([]);
                    setAllProcessedResumes([]);
                    setShortlistedResumeNames([]);
                    setNonShortlistedResumeNames([]);
                }
            } catch (err) {
                setError(err.message);
                console.error("Error checking processing status:", err);
            }
        };

        const interval = setInterval(checkProcessingStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleResumeUpload = async (event) => {
        const files = Array.from(event.target.files);
        setError(null);
        setUploadProgress(0);
        
        try {
            for (let i = 0; i < files.length; i++) {
                await uploadResume(files[i]);
                setUploadProgress(((i + 1) / files.length) * 100);
            }
            setResumes([...resumes, ...files]);
            setUploadProgress(0);
        } catch (err) {
            setError(err.message);
            setUploadProgress(0);
        }
    };

    const handleJobDescriptionUpload = async (event) => {
        const file = event.target.files[0];
        setError(null);
        setUploadProgress(0);
        
        try {
            await uploadJobDescription(file);
            setJobDescription(file);
            setProcessing(true);
            setUploadProgress(100);
            setTimeout(() => setUploadProgress(0), 1000);
            setResults([]); // Clear previous results to show processing status
            setAllProcessedResumes([]);
            setShortlistedResumeNames([]);
            setNonShortlistedResumeNames([]);
        } catch (err) {
            setError(err.message);
            setUploadProgress(0);
        }
    };

    return (
        <div className="resume-uploader">
            <div className="upload-container">
                <div className="upload-section">
                    <h3>Upload Resumes</h3>
                    <div className="file-input-container">
                        <input
                            type="file"
                            multiple
                            accept=".pdf,.doc,.docx"
                            onChange={handleResumeUpload}
                            id="resume-upload"
                            className="file-input"
                        />
                        <label htmlFor="resume-upload" className="file-input-label">
                            Choose Files
                        </label>
                    </div>
                    <p className="upload-count">Uploaded Resumes: {resumes.length}</p>
                    {uploadProgress > 0 && (
                        <div className="progress-bar">
                            <div 
                                className="progress-bar-fill"
                                style={{ width: `${uploadProgress}%` }}
                            />
                        </div>
                    )}
                </div>
                
                <div className="upload-section">
                    <h3>Upload Job Description</h3>
                    <div className="file-input-container">
                        <input
                            type="file"
                            accept=".pdf,.doc,.docx,.txt,.csv"
                            onChange={handleJobDescriptionUpload}
                            id="jd-upload"
                            className="file-input"
                        />
                        <label htmlFor="jd-upload" className="file-input-label">
                            Choose File
                        </label>
                    </div>
                    {jobDescription && (
                        <p className="file-name">Job Description: {jobDescription.name}</p>
                    )}
                </div>
            </div>
            
            {processing && (
                <div className="processing-status">
                    <div className="spinner"></div>
                    <p>Processing resumes... Please wait.</p>
                </div>
            )}
            
            {error && (
                <div className="error">
                    <p>Error: {error}</p>
                </div>
            )}
            
            <div className="processed-resumes-summary">
                {shortlistedResumeNames.length > 0 && (
                    <div className="shortlisted-section">
                        <h3>Shortlisted Resumes (Top 3)</h3>
                        <ul>
                            {shortlistedResumeNames.map((name, index) => (
                                <li key={index}>{name}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {nonShortlistedResumeNames.length > 0 && (
                    <div className="non-shortlisted-section">
                        <h3>Other Processed Resumes</h3>
                        <ul>
                            {nonShortlistedResumeNames.map((name, index) => (
                                <li key={index}>{name}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {results.length > 0 && ( // Only show detailed results for the top 3
                <div className="results">
                    <h3>Detailed Match Visualizations (Top 3)</h3>
                    {results.map((result, index) => (
                        <div key={index} className="result-item">
                            <h4>{result.results[0].Candidate}</h4> {/* Display candidate name */}
                            <div className="result-content">
                                <div className="result-images">
                                    <div className="image-container">
                                        <h5>Match Graph</h5>
                                        <img src={result.graphUrl} alt="Graph" />
                                    </div>
                                    <div className="image-container">
                                        <h5>Word Cloud</h5>
                                        <img src={result.wordcloudUrl} alt="Wordcloud" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ResumeUploader; 