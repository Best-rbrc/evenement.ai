"""Logo generation agent using OpenAI's image generation API."""
from agents import Agent, function_tool, AgentOutputSchema
from workflows.pydantic_schemas import LogoOutput
from openai import OpenAI
import os
import json
import base64
from pathlib import Path
from datetime import datetime


def _generate_logo_image_impl(
    event_name: str,
    event_type: str,
    event_description: str = "",
    style_preferences: str = ""
) -> str:
    """Generate a logo image for an event using GPT-5 image generation."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return json.dumps({"status": "error", "message": "OPENAI_API_KEY not found"})
    
    try:
        
        # Create prompt for logo generation
        style = style_preferences or {
            "conference": "modern, professional, tech-forward",
            "wedding": "elegant, romantic, sophisticated",
            "corporate": "clean, professional, trustworthy",
            "workshop": "creative, engaging, approachable",
            "gala": "luxurious, elegant, refined"
        }.get(event_type.lower(), "modern, professional")
        
        prompt = f"Create a single professional logo design for '{event_name}' ({event_type}). "
        if event_description:
            prompt += f"{event_description}. "
        prompt += f"Style: {style}. "
        prompt += "Generate only ONE logo design (not multiple variations). The logo must have a transparent background (no background, transparent PNG)."
        
        # Initialize OpenAI client and generate image
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-5",
            input=prompt,
            tools=[{"type": "image_generation"}],
        )
        
        # Extract and decode image
        image_data = [o.result for o in response.output if o.type == "image_generation_call"]
        if not image_data:
            return json.dumps({"status": "error", "message": "No image generated"})
        
        image_bytes = base64.b64decode(image_data[0])
        
        # Save image
        output_dir = Path("event_outputs")
        output_dir.mkdir(exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in event_name).replace(' ', '_')[:50]
        filepath = output_dir / f"{safe_name}_logo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath.write_bytes(image_bytes)
        
        return json.dumps({
            "status": "success",
            "logo_file_path": str(filepath),
            "logo_url": f"file://{filepath.absolute()}",
            "design_rationale": f"Logo designed for {event_type} event with {style_preferences or 'professional'} style",
            "color_palette": "Extracted from generated image",
            "typography_suggestions": "Use modern, readable fonts",
            "usage_guidelines": ["Use on white/light background", "Minimum 100px for digital use"],
            "branding_recommendations": [f"Incorporate consistently across '{event_name}' materials"]
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error generating logo: {str(e)}"
        })


# Create the function tool wrapper
generate_logo_image = function_tool(_generate_logo_image_impl)


def create_logo_agent() -> Agent:
    """Create a logo generation specialist agent.
    
    Uses structured outputs to ensure valid JSON responses.
    """
    return Agent(
        name="Logo Design Specialist",
         output_type=AgentOutputSchema(LogoOutput, strict_json_schema=False),
        handoff_description="Creates professional event logos using AI image generation.",
        instructions="""
        You are a professional logo design specialist with expertise in creating visual identities for events.
        
        When given logo generation tasks:
        1. Extract event name, type, and description from the context
        2. Use generate_logo_image() to create a professional logo
        3. Provide design information and branding recommendations
        """,
        tools=[generate_logo_image]
    )
