import requests
from dotenv import load_dotenv
import os
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse

load_dotenv()
app = FastAPI()

ai_api_key = os.getenv('groq_api_key')
profile_link = "https://www.linkedin.com/in/basil-vazhathottathil-a540a821b/"

@app.get("/")
def read_root():
    return {"message": "this shit works"}

def get_linkedin_profile(profile_link, include_skills=True, include_certifications=True, include_experience=True):
    url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-linkedin-profile-by-salesnavurl"

    querystring = {
        "linkedin_url": profile_link,
        "include_skills": str(include_skills).lower(),
        "include_certifications": str(include_certifications).lower(),
        "include_experience": str(include_experience).lower(),
        "include_publications": "false",
        "include_honors": "false",
        "include_volunteers": "false",
        "include_projects": "false",
        "include_patents": "false",
        "include_courses": "false",
        "include_organizations": "false"
    }

    headers = {
        "x-rapidapi-key": "d7e4a4a14fmsh5ce47c9b33e757fp1ab922jsnf462e4183ea0",
        "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def send_to_groq(profile_data, job_criteria):
    headers = {
        "Authorization": f"Bearer {ai_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Check if the given data from a LinkedIn profile is suitable for given positions."},
            {"role": "user", "content": f"Profile Data: {profile_data}\nJob Criteria: {job_criteria}"}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        ai_response = response.json()["choices"][0]["message"]["content"]
        return ai_response
    except requests.exceptions.RequestException as e:
        print("Error contacting AI API:", e)
        return None

@app.post("/getresponse")
def main():
    profile_data = get_linkedin_profile(profile_link, include_skills=True, include_certifications=True, include_experience=True)
    print("Profile Data:", profile_data)

    # Load job criteria from JSON file
    with open('post_details.json', 'r') as file:
        job_criteria = json.load(file)

    # Collect AI responses
    ai_responses = {}
    for job in job_criteria["job_positions"]:
        ai_response = send_to_groq(profile_data, job["criteria"])
        ai_responses[job['title']] = ai_response

    return JSONResponse(content=ai_responses)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)