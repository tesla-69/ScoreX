from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import pandas as pd
import os
from typing import List, Dict, Any
from pydantic import BaseModel
from . import db
import subprocess
import sys
import asyncio
import traceback

app = FastAPI(title="Resume Parser API")

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchResult(BaseModel):
    Area: str
    Match: float
    Matching_Keywords: str
    Missing_Keywords: str

class MatchResponse(BaseModel):
    results: List[Dict[str, Any]]
    graphUrl: str
    wordcloudUrl: str

# Get absolute path to ../data relative to current script
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

async def run_model():
    """Run the model processing script"""
    try:
        # Get the absolute path to the model directory
        model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
        
        # Run model.py as a subprocess, ensuring it executes from the correct directory
        print(f"Attempting to run model.py from directory: {model_dir}")
        process = await asyncio.create_subprocess_exec(
            sys.executable, "model.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=model_dir # Set the working directory for the subprocess
        )
        
        stdout, stderr = await process.communicate()
        
        stdout_decoded = stdout.decode().strip()
        stderr_decoded = stderr.decode().strip()
        
        print(f"model.py stdout:\n{stdout_decoded}")
        print(f"model.py stderr:\n{stderr_decoded}")
        print(f"model.py return code: {process.returncode}")

        if process.returncode != 0:
            # If there's an error and stderr has content, print it more clearly
            if stderr_decoded:
                print(f"Error running model.py: {stderr_decoded}")
            else:
                print(f"model.py exited with non-zero code {process.returncode} but no stderr output.")
            return False
            
        print("Model processing completed successfully via FastAPI background task")
        return True
        
    except Exception as e:
        print(f"Error in run_model (subprocess execution): {str(e)}")
        traceback.print_exc() # Added for detailed traceback
        return False

@app.post("/api/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file"""
    try:
        contents = await file.read()
        resume_id = await db.save_resume(contents, file.filename, file.content_type)
        return {"status": "success", "message": "Resume uploaded successfully", "id": str(resume_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/job-description")
async def upload_job_description(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a job description and trigger model processing"""
    try:
        contents = await file.read()
        jd_id = await db.save_job_description(contents, file.filename, file.content_type)
        
        # Trigger model processing in background
        background_tasks.add_task(run_model)
        
        return {"status": "success", "message": "Job description uploaded and processing started", "id": str(jd_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/processing-status")
async def get_processing_status():
    """Get the current processing status"""
    try:
        unprocessed_resumes = len(db.get_unprocessed_resumes())
        latest_jd = db.get_latest_job_description()
        
        return {
            "status": "success",
            "unprocessed_resumes": unprocessed_resumes,
            "has_job_description": latest_jd is not None,
            "is_processing": unprocessed_resumes > 0 and latest_jd is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "success", "message": "Resume Parser API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "success", "message": "API is healthy"}

@app.get("/api/results/{match_number}")
async def get_match_results(match_number: int):
    if not 1 <= match_number <= 3:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid match number"}
        )
    
    match_folder = os.path.join(ROOT_DIR, f"match/match{match_number}")
    results_file = os.path.join(match_folder, 'results.csv')
    
    try:
        print(f"Reading results from: {results_file}")
        if not os.path.exists(results_file):
            return JSONResponse(
                status_code=404,
                content={"status": "error", "detail": f"Results file not found at {results_file}"}
            )
            
        results_df = pd.read_csv(results_file)
        results = results_df.to_dict('records')
        
        response_data = {
            "status": "success",
            "results": results,
            "graphUrl": f"/api/graph/{match_number}",
            "wordcloudUrl": f"/api/wordcloud/{match_number}"
        }
        print(f"Sending response: {response_data}")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except Exception as e:
        print(f"Error in get_match_results: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

@app.get("/api/graph/{match_number}")
async def get_graph(match_number: int):
    if not 1 <= match_number <= 3:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid match number"}
        )
    
    file_path = os.path.join(ROOT_DIR, f"match/match{match_number}", "graph.png")
    print(f"Serving graph from: {file_path}")
    
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "detail": f"Graph not found at {file_path}"}
        )
    
    return FileResponse(file_path, media_type="image/png")

@app.get("/api/wordcloud/{match_number}")
async def get_wordcloud(match_number: int):
    if not 1 <= match_number <= 3:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "detail": "Invalid match number"}
        )
    
    file_path = os.path.join(ROOT_DIR, f"match/match{match_number}", "wordcloud.png")
    print(f"Serving wordcloud from: {file_path}")
    
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "detail": f"Wordcloud not found at {file_path}"}
        )
    
    return FileResponse(file_path, media_type="image/png")

@app.get("/api/top-matches")
async def get_top_matches():
    try:
        output_file = os.path.join(ROOT_DIR, 'output.csv')
        print(f"Reading top matches from: {output_file}")
        
        if not os.path.exists(output_file):
            return JSONResponse(
                status_code=404,
                content={"status": "error", "detail": f"Output file not found at {output_file}"}
            )
            
        df = pd.read_csv(output_file)
        candidates = df['Candidate'].unique()
        
        response_data = {
            "status": "success",
            "candidates": candidates.tolist()
        }
        print(f"Sending response: {response_data}")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except Exception as e:
        print(f"Error in get_top_matches: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    print(f"Project root directory: {ROOT_DIR}")
    print(f"Checking files:")
    print(f"output.csv exists: {os.path.exists(os.path.join(ROOT_DIR, 'output.csv'))}")
    for i in range(1, 4):
        match_dir = os.path.join(ROOT_DIR, f"match/match{i}")
        print(f"match{i} exists: {os.path.exists(match_dir)}")
        if os.path.exists(match_dir):
            print(f"  results.csv exists: {os.path.exists(os.path.join(match_dir, 'results.csv'))}")
            print(f"  graph.png exists: {os.path.exists(os.path.join(match_dir, 'graph.png'))}")
            print(f"  wordcloud.png exists: {os.path.exists(os.path.join(match_dir, 'wordcloud.png'))}")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 