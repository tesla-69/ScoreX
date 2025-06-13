export const uploadFiles = async (resumes, jd) => {
    const formData = new FormData();
    
    // Add resumes
    resumes.forEach(resume => {
        formData.append('resumes', resume);
    });
    
    // Add JD if present
    if (jd) {
        formData.append('jd', jd);
    }
    
    try {
        const response = await fetch('http://localhost:8000/api/upload', {
            method: 'POST',
            body: formData,
            // Don't set Content-Type header, let the browser set it with the boundary
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `Upload failed with status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('Upload failed:', error);
        throw new Error(error.message || 'Failed to upload files. Please try again.');
    }
};