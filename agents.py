from typing import Dict, List, Any
from agents import Agent
from agents.tools import ToolContext
from google import genai
from google.genai import types
import re
import random

# --- Mock Data and Stubs ---
SAMPLE_IMAGE_METADATA = [
    {
        "image_uri": "gs://site_comparisons/Project_images/Project_Aug_1.png",
        "date": "2023-08-13",
        "other_metadata": {"cloud_cover": 0.2},
    },
    {
        "image_uri": "gs://site_comparisons/Project_images/Project_Nov_1.png",
        "date": "2023-11-29",
        "other_metadata": {"cloud_cover": 0.1},
    },
    {
        "image_uri": "gs://site_comparisons/Project_images/Project_Dec_1.png",
        "date": "2023-12-08",
        "other_metadata": {"cloud_cover": 0.1},
    },
]


# --- Tool Functions ---
def get_project_details(tool_context: ToolContext) -> Dict[str, Any]:
    """Gathers project details from the user."""
    project_name = input("Enter project name: ")
    project_type = input("Enter project type (e.g., building, road): ")
    return {"project_name": project_name, "project_type": project_type}


def get_image_metadata(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves image metadata from a JSON record (replace with actual retrieval)."""
    print("Retrieving image metadata...")
    return {"image_metadata": SAMPLE_IMAGE_METADATA}


def analyze_image(
        tool_context: ToolContext,
        image_metadata_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Analyzes multiple images using Gemini.

    Args:
        tool_context: The ToolContext object.
        image_metadata_list: A list of dictionaries containing at least a 'gcs_uri' or 'image_uri'.

    Returns:
        A list of dictionaries, each containing the analysis results and progress estimate for an image.
    """
    analysis_results = []
    for image_metadata in image_metadata_list:
        image_uri = image_metadata['image_uri']
        try:
            # If the external API is available, use it.
            client = genai.Client(vertexai=True, project="platinum-banner-303105", location="us-central1")
            image1 = types.Part.from_uri(
                file_uri=image_uri,
                mime_type="image/png",
            )
            prompt_text = (
                f"Analyze this satellite image of a construction site for a {project_details.get('project_type', 'construction project')}.\n"
                f"Consider the current state of progress, potential issues, and the overall timeline. Provide specific details about what you observe in the image.\n"
                f"The project name is {project_details.get('project_name', 'unknown')}."
            )
            text1 = types.Part.from_text(text=prompt_text)
            model = "gemini-2.0-flash-001"
            contents = [types.Content(role="user", parts=[image1, text1])],
            generate_content_config = types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.95,
                max_output_tokens=4024,
                response_modalities=["TEXT"],
                safety_settings = [types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="OFF"
                ),types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )]
            )
            response_text = ""
            for chunk in client.models.generate_content_stream(
                    model=model, contents=contents, config=generate_content_config
            ):
                response_text += chunk.text

        except Exception as e:
            # Simulate analysis if the Gemini API call fails.
            print(f"Error with Gemini client for image {image_uri}: {e}. Using simulated analysis.")
            # Simulate a dummy progress percentage between 50 and 100.
            simulated_progress = random.uniform(50, 100)
            response_text = (
                f"Simulated analysis for image {image_uri}. The site appears to be at approximately "
                f"{simulated_progress:.1f}% progress with visible structural developments."
            )

        # Extract progress percentage using regex
        progress_match = re.search(r"(\d+(\.\d+)?)\s*%?", response_text)
        progress_estimate = float(progress_match.group(1)) if progress_match else 0.0

        # Append the analysis for the current image
        analysis_results.append({"analysis": response_text, "progress": progress_estimate})

    return analysis_results


def consolidate_analysis(tool_context: ToolContext, image_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Consolidates individual image analyses into a timeline."""
    print("Consolidating analysis from individual images...")
    timeline = []
    total_progress = 0.0
    num_analyses = len(image_analyses)

    for analysis in image_analyses:
        timeline.append({"analysis": analysis["analysis"], "progress": analysis["progress"]})
        total_progress += analysis["progress"]

    overall_progress = total_progress / num_analyses if num_analyses > 0 else 0.0

    # Basic estimated completion (improve with more sophisticated logic)
    estimated_completion = "2024-06-01"  # Replace with actual calculation

    return {
        "timeline": timeline,
        "overall_progress": overall_progress,
        "estimated_completion": estimated_completion,
    }


def recommend_image_specs(tool_context: ToolContext, project_type: str) -> Dict[str, Any]:
    """Recommends specifications and frequency for satellite imagery."""
    print(f"Recommending image specifications for project type: {project_type}")
    if project_type.lower() == "building":
        recommendations = {"frequency": "monthly", "resolution": "0.5m", "spectral_bands": ["RGB", "NIR"]}
    elif project_type.lower() == "road":
        recommendations = {"frequency": "bi-weekly", "resolution": "1m", "spectral_bands": ["RGB"]}
    else:
        recommendations = {"frequency": "monthly", "resolution": "1m", "spectral_bands": ["RGB"]}
    return {"recommendations": recommendations}


def order_images(tool_context: ToolContext, recommendations: Dict[str, Any]) -> Dict[str, Any]:
    """Orders satellite images based on given specifications (replace with Earth Engine API calls)."""
    print(f"Ordering images with specifications: {recommendations}")
    # Simulate ordering process.
    simulated_order_id = f"order_{random.randint(1000,9999)}"
    print(f"Image order placed successfully with order ID: {simulated_order_id}")
    return {"order_status": "placed", "order_id": simulated_order_id}


# --- Agents ---

image_analyzer_agent = Agent(
    name="image_analyzer_agent",
    model="gemini-2.0-flash-001",
    tools=[analyze_image],
    instruction="""Using the tool provided collect the image analysis. The image analysis should be verbose and give a lot of details on the current status and progress and reasons for % progress. Send the tool a list of the "image_uri" from the retrieved metadata""",
)

progress_estimator_agent = Agent(
    name="progress_estimator_agent",
    model="gemini-1.5-flash-002",
    tools=[consolidate_analysis],
    instruction="""Consolidate the image analyses, estimate the overall project progress and remaining time using the tool provided.""",
)

project_details_and_images_agent = Agent(
    name="progress_estimator_agent",
    model="gemini-1.5-pro-002",
    tools=[get_project_details,get_image_metadata,],
    instruction="""Get the project details and the image metadata and image_uri using the tools supplied""",
)

future_images_agent = Agent(
    name="progress_estimator_agent",
    model="gemini-1.5-flash-002",
    tools=[recommend_image_specs,order_images,],
    instruction="""Using the tolls provided recommend the types of images that are required to continue to monitor the status of the project with increasing frequency as the project comes to a close and order those images.""",
)

# --- Main Agent ---

construction_analysis_agent = Agent(
    name="construction_analysis_agent",
    model="gemini-1.5-flash-002",
    flow="sequential",
    children=[project_details_and_images_agent, image_analyzer_agent, progress_estimator_agent, future_images_agent],
    tools=[],
    instruction=(
        "You are an agent to analyze construction site progress. First, get the project details from the user. "
        "Then, retrieve image metadata. Use the image_analyzer_agent to analyze each image. Consolidate the analysis "
        "using the progress_estimator_agent. Finally, recommend image specifications and order new images. "
        "Generate a report, with a brief summary of each image, a timeline across them with progress status and a summary "
        "of next steps including new images."
    ),
)

root_agent = construction_analysis_agent
