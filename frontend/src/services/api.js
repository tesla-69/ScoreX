const API_BASE_URL = 'http://localhost:8000/api';

export const uploadResume = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload/resume`, {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error('Failed to upload resume');
    }
    
    return response.json();
};

export const uploadJobDescription = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload/job-description`, {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error('Failed to upload job description');
    }
    
    return response.json();
};

export const getProcessingStatus = async () => {
    const response = await fetch(`${API_BASE_URL}/processing-status`);
    
    if (!response.ok) {
        throw new Error('Failed to get processing status');
    }
    
    return response.json();
};

export const getMatchResults = async (matchNumber) => {
    const response = await fetch(`${API_BASE_URL}/results/${matchNumber}`);
    
    if (!response.ok) {
        throw new Error('Failed to get match results');
    }
    
    return response.json();
};

export const getGraph = async (matchNumber) => {
    const response = await fetch(`${API_BASE_URL}/graph/${matchNumber}`);
    
    if (!response.ok) {
        throw new Error('Failed to get graph');
    }
    
    return response.blob();
};

export const getWordcloud = async (matchNumber) => {
    const response = await fetch(`${API_BASE_URL}/wordcloud/${matchNumber}`);
    
    if (!response.ok) {
        throw new Error('Failed to get wordcloud');
    }
    
    return response.blob();
};

export const getTopMatches = async () => {
    const response = await fetch(`${API_BASE_URL}/top-matches`);
    
    if (!response.ok) {
        throw new Error('Failed to get top matches');
    }
    
    return response.json();
}; 