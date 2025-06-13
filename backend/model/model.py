import os
import PyPDF2
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from mongo_utils import get_resumes_from_mongodb, cleanup_temp_files

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ' '.join([page.extract_text() for page in reader.pages])

def preprocess(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    return re.sub(r'\s+', ' ', text).strip()

def read_jd_from_csv(csv_path):
    df = pd.read_csv(csv_path)
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

def main():
    jd_csv_path = "../data/jd.csv"
    output_csv_path = "../data/output.csv"
    jd_areas = read_jd_from_csv(jd_csv_path)

    # Get resumes from MongoDB
    resumes = get_resumes_from_mongodb()
    
    try:
        # Process all resumes from MongoDB
        candidates = []
        for resume_data in resumes:
            candidates.append(process_candidate(resume_data, jd_areas))

        # Sort candidates by average match percentage and take top 3
        top_candidates = sorted(candidates, key=lambda x: -x['avg_match'])[:3]

        # Create output folders under ../match/
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
        pd.DataFrame(all_results).to_csv(output_csv_path, index=False)
        print(f"Combined results saved to {output_csv_path}")

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

    finally:
        # Clean up temporary files
        cleanup_temp_files(resumes)

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
    main()
