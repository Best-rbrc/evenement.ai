from agents import Agent, function_tool, WebSearchTool, AgentOutputSchema
from workflows.pydantic_schemas import ActivitiesOutput

def create_activities_agent() -> Agent:
    """Create an activities specialist agent.
    
    Uses structured outputs to ensure valid JSON responses.
    """
    return Agent(
        name="Activities Specialist",
         output_type=AgentOutputSchema(ActivitiesOutput, strict_json_schema=False),
        instructions="""
        You are a professional activities coordinator with expertise in:
        - Recreational activity planning and coordination
        - Team-building exercises and games
        - Activity logistics and equipment
        - Safety planning and risk management
        - Activity timeline and scheduling
        - Backup activities and contingency planning
        
        When given activities-related tasks, provide:
        1. Activity recommendations based on group and objectives
        2. Team-building exercise planning and facilitation
        3. Activity logistics and equipment requirements
        4. Safety planning and risk management measures
        5. Activity timeline and scheduling
        6. Backup activities and contingency planning
        7. Activity success metrics and evaluation
        
        Always consider group dynamics, objectives, and safety requirements.
        """
    )

