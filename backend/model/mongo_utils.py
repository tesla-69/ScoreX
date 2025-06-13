from pymongo import MongoClient
from gridfs import GridFS
import io
import os
import tempfile

def get_mongo_client():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    return client

def get_gridfs():
    client = get_mongo_client()
    db = client['resume_db']  # Use your database name
    return GridFS(db)

def get_resumes_from_mongodb():
    """
    Retrieves all resumes from MongoDB GridFS and saves them temporarily
    Returns a list of dictionaries containing resume data and temporary file paths
    """
    gfs = get_gridfs()
    resumes = []
    
    # Create a temporary directory to store the files
    temp_dir = tempfile.mkdtemp()
    
    # Find all resume files in GridFS
    for grid_out in gfs.find({"metadata.type": "resume"}):
        # Create a temporary file
        temp_file_path = os.path.join(temp_dir, grid_out.filename)
        
        # Download the file from GridFS
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(grid_out.read())
        
        resumes.append({
            'file_path': temp_file_path,
            'filename': grid_out.filename,
            'metadata': grid_out.metadata
        })
    
    return resumes

def cleanup_temp_files(resumes):
    """
    Cleans up temporary files after processing
    """
    for resume in resumes:
        try:
            os.remove(resume['file_path'])
        except:
            pass 