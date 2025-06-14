import os
import PyPDF2
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from mongo_utils import get_resumes_from_mongodb, cleanup_temp_files, get_unprocessed_resumes, get_latest_job_description, mark_resume_processed, mark_job_description_processed
import tempfile
import sys
import traceback # Import traceback for detailed error logging

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ' '.join([page.extract_text() for page in reader.pages])

def preprocess(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    return re.sub(r'\s+', ' ', text).strip()

def read_jd_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='latin-1') # Try common alternative encoding
    except Exception as e:
        print(f"Error reading JD CSV file: {e}")
        raise # Re-raise if it's another error
    
    # Filter and create a dictionary from specific fields as needed for your model
    return {row["Field"]: row["Details"] for _, row in df.iterrows() 
            if row["Field"] in ["Job Description", "Key Responsibilities", 
                               "Required Qualifications", "Preferred Qualifications"]}

def analyze_keywords(jd_text, resume_text, top_n=15):
    vectorizer = TfidfVectorizer(stop_words='english')
    jd_tfidf = vectorizer.fit_transform([jd_text])
    features = vectorizer.get_feature_names_out()
    jd_scores = jd_tfidf.toarray()[0]
    top_keywords = [features[i] for i in jd_scores.argsort()[::-1][:top_n]]
    resume_words = set(resume_text.split())
    return (
        [kw for kw in top_keywords if kw in resume_words],
        [kw for kw in top_keywords if kw not in resume_words]
    )

def process_candidate(resume_data, jd_areas):
    resume_clean = preprocess(extract_text_from_pdf(resume_data['file_path']))
    results = []
    all_matching_keywords = []
    all_missing_keywords = []
    for area, jd_text in jd_areas.items():
        jd_clean = preprocess(jd_text)
        vectorizer = TfidfVectorizer()
        similarity = cosine_similarity(
            vectorizer.fit_transform([jd_clean]),
            vectorizer.transform([resume_clean])
        )[0][0] * 100
        match_kw, missing_kw = analyze_keywords(jd_clean, resume_clean)
        all_matching_keywords.extend(match_kw)
        all_missing_keywords.extend(missing_kw)
        results.append({
            "Area": area,
            "Match %": round(similarity, 2),
            "Matching Keywords": ", ".join(match_kw[:5]),
            "Missing Keywords": ", ".join(missing_kw[:5])
        })
    avg_match = sum(r["Match %"] for r in results) / len(results)
    return {
        "resume_path": resume_data['file_path'],
        "filename": resume_data['filename'],
        "results": results,
        "avg_match": avg_match,
        "matching_keywords": all_matching_keywords,
        "missing_keywords": all_missing_keywords
    }

def process_resumes():
    """Process resumes from MongoDB and generate results"""
    try:
        # Get unprocessed resumes and latest job description using mongo_utils
        resumes = get_unprocessed_resumes()
        job_description = get_latest_job_description()
        
        if not resumes or not job_description:
            print("No unprocessed resumes or job description found")
            return False
            
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save job description to temp file (as CSV)
            jd_path = os.path.join(temp_dir, "job_description.csv")
            with open(jd_path, "wb") as f:
                f.write(job_description["data"])
            
            # Save resumes to temp files
            resume_paths = []
            for resume in resumes:
                resume_path = os.path.join(temp_dir, resume["filename"])
                with open(resume_path, "wb") as f:
                    f.write(resume["data"])
                resume_paths.append(resume_path)
            
            # Read JD areas from the uploaded CSV
            jd_areas = read_jd_from_csv(jd_path)
            
            # Process resumes
            candidates = []
            for resume_data, resume_path in zip(resumes, resume_paths):
                candidate_data = {
                    'file_path': resume_path,
                    'filename': resume_data['filename']
                }
                candidates.append(process_candidate(candidate_data, jd_areas))
            
            # Sort candidates by average match percentage and take top 3
            top_candidates = sorted(candidates, key=lambda x: -x['avg_match'])[:3]
            
            # Create output folders under ../data/match/
            output_folders = []
            for i in range(1, 4):
                folder = os.path.join("..","data", "match", f"match{i}")
                os.makedirs(folder, exist_ok=True)
                output_folders.append(folder)
                print(f"Created output folder: {folder}")
            
            # Save combined results for top 3 to CSV
            all_results = []
            for idx, candidate in enumerate(top_candidates):
                for result in candidate['results']:
                    all_results.append({
                        "Candidate": candidate['filename'],
                        **result
                    })
            pd.DataFrame(all_results).to_csv(os.path.join("..", "data", "output.csv"), index=False)
            print(f"Combined results saved to ../data/output.csv")
            
            # Save individual candidate results and generate visualizations
            for idx, (candidate, folder) in enumerate(zip(top_candidates, output_folders), 1):
                candidate_name = candidate['filename']
                pd.DataFrame(candidate['results']).to_csv(os.path.join(folder, f"results.csv"), index=False)
                print(f"Individual results for {candidate_name} saved to {folder}/results.csv")

                # Generate visualizations
                generate_visualizations(
                    candidate['matching_keywords'],
                    candidate['missing_keywords'],
                    candidate_name,
                    candidate['results'],
                    folder
                )

            # Mark resumes and job description as processed using mongo_utils
            for resume in resumes:
                mark_resume_processed(resume['_id'])
            mark_job_description_processed(job_description['_id'])
            
            return True
            
    except Exception as e:
        print(f"Error in process_resumes: {str(e)}")
        traceback.print_exc()
        return False

def generate_visualizations(matching_keywords, missing_keywords, candidate_name, results, output_folder):
    """Generate visualizations for a resume"""
    # Word clouds
    matching_text = ' '.join(matching_keywords)
    missing_text = ' '.join(missing_keywords)
    if matching_text and missing_text:
        plt.figure(figsize=(15, 6))
        plt.subplot(1, 2, 1)
        wc_match = WordCloud(width=600, height=400, background_color='white',
                           colormap='Greens').generate(matching_text)
        plt.imshow(wc_match, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Matching Keywords - {candidate_name}', fontsize=16, fontweight='bold')
        plt.subplot(1, 2, 2)
        wc_missing = WordCloud(width=600, height=400, background_color='white',
                             colormap='Reds').generate(missing_text)
        plt.imshow(wc_missing, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Missing Keywords - {candidate_name}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, 'wordcloud.png'), dpi=300, bbox_inches='tight')
        plt.close()

    # Bar chart
    df_results = pd.DataFrame(results)
    plt.figure(figsize=(12, 8))
    bars = plt.bar(df_results['Area'], df_results['Match %'], color='skyblue', edgecolor='navy', linewidth=1.2)
    for bar, percentage in zip(bars, df_results['Match %']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{percentage}%', ha='center', va='bottom', fontweight='bold')
    plt.ylim(0, 100)
    plt.ylabel('Match Percentage (%)', fontsize=12, fontweight='bold')
    plt.xlabel('Job Description Fields', fontsize=12, fontweight='bold')
    plt.title(f'Resume Match Percentage by JD Field - {candidate_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, 'graph.png'), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    success = process_resumes()
    sys.exit(0 if success else 1)
