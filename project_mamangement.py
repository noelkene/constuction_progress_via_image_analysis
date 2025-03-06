import streamlit as st
from typing import Dict, List, Any
import random
import re

from google import genai
from google.genai import types

SAMPLE_IMAGE_METADATA = [
    {
        "image_uri": "https://storage.googleapis.com/site_comparisons/Project_images/Project_Aug_1.png",
        "date": "2023-08-13",
        "other_metadata": {"cloud_cover": 0.2},
    },
    {
        "image_uri": "https://storage.googleapis.com/site_comparisons/Project_images/Project_Nov_1.png",
        "date": "2023-11-29",
        "other_metadata": {"cloud_cover": 0.1},
    },
    {
        "image_uri": "https://storage.googleapis.com/site_comparisons/Project_images/Project_Dec_1.png",
        "date": "2023-12-08",
        "other_metadata": {"cloud_cover": 0.1},
    },
]

# Analysis function using Gemini
def analyze_images(image_metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    analysis_results = []
    client = genai.Client(vertexai=True, project="platinum-banner-303105", location="us-central1")
    model = "gemini-2.0-flash-001"

    for image_metadata in image_metadata_list:
        image_uri = image_metadata['image_uri']
        image1 = types.Part.from_uri(
            file_uri=image_uri,
            mime_type="image/png",
        )
        prompt_text = (
            f"Analyze this satellite image of a construction site. "
            f"Consider the current state of progress, potential issues, and the overall timeline. "
            f"Provide specific details about what you observe in the image."
        )
        text1 = types.Part.from_text(text=prompt_text)
        contents = [types.Content(role="user", parts=[image1, text1])]

        generate_content_config = types.GenerateContentConfig(
            temperature=0.2,
            top_p=0.95,
            max_output_tokens=4024,
            response_modalities=["TEXT"],
        )

        response_text = ""
        try:
            for chunk in client.models.generate_content_stream(
                    model=model, contents=contents, config=generate_content_config
            ):
                response_text += chunk.text
        except Exception as e:
            print(f"Error with Gemini client for image {image_uri}: {e}. Using simulated analysis.")
            simulated_progress = random.uniform(50, 100)
            response_text = (
                f"Simulated analysis for image {image_uri}. The site appears to be at approximately "
                f"{simulated_progress:.1f}% progress with visible structural developments."
            )

        progress_match = re.search(r"(\d+(\.\d+)?)\s*%?", response_text)
        progress_estimate = float(progress_match.group(1)) if progress_match else 0.0

        analysis_results.append({"image_uri": image_uri, "description": response_text, "progress": progress_estimate})
    return analysis_results

# Function to generate executive summary using Gemini
def generate_executive_summary(analysis_results: List[Dict[str, Any]]) -> str:
    client = genai.Client(vertexai=True, project="platinum-banner-303105", location="us-central1")
    model = "gemini-1.5-pro-002"
    summary_prompt = (
        f"""Provide an executive summary for a construction project. Highlight the % of the project completed and estimation of time to finish the project. 
        {analysis_results}
        Include key observations from the image analysis, potential risks, and strategic recommendations, including the frequency of satellite imagery needed for continued monitoring."""
    )

    response_text = ""
 #   try:
    for chunk in client.models.generate_content_stream(
            model=model, contents=summary_prompt
    ):
        response_text += chunk.text


 #   except Exception as e:
 #       response_text = f"Simulated executive summary: The project is approximately {overall_progress:.1f}% complete. It is recommended to increase the frequency of satellite imagery to weekly as the project nears completion."

    return response_text

# Streamlit app
st.title("Construction Project Status Analyzer")

st.header("Project Images")
for image in SAMPLE_IMAGE_METADATA:
    st.image(image["image_uri"], caption=f"Image from {image['date']} - Cloud Cover: {image['other_metadata']['cloud_cover'] * 100}%")

if st.button("Analyze Project Status", key="analyze_button"):
    analysis_results = analyze_images(SAMPLE_IMAGE_METADATA)
    st.header("Analysis Results")
    total_progress = 0
    for result in analysis_results:
        st.image(result["image_uri"], caption=result["description"])
        total_progress += result["progress"]
    st.subheader("Executive Summary")
    executive_summary = generate_executive_summary(analysis_results)
    st.write(executive_summary)
