# Quick Reference: Schema Validation System

## How It Works

### Before (Manual JSON Parsing)
```python
# Agent returns string
result = agent.run(prompt)
output = json.loads(result.final_output)  # Can fail!

# Manual validation
if "summary" not in output:
    raise ValueError("Missing summary")
```

### After (Structured Outputs)
```python
# Agent with  output_type
agent = Agent(
    name="Venue Specialist",
     output_type=VenueOutput,  # Pydantic model
    instructions="..."
)

# Result is automatically valid
result = agent.run(prompt)
output = result.final_output.model_dump()  # Always valid dict
```

## Adding a New Field to a Schema

### 1. Update Pydantic Model
```python
# workflows/pydantic_schemas.py
class VenueOutput(BaseModel):
    summary: str
    venues: List[VenueOption]
    # Add new field
    sustainability_rating: Optional[str] = Field(
        None, 
        description="Sustainability rating of venue options"
    )
```

### 2. Update Agent Instructions (Optional)
```python
# custom_agents/venue_agent.py
instructions="""
...
Include sustainability ratings where available.
..."""
```

That's it! OpenAI enforces the schema automatically.

## Common Patterns

### Required Field
```python
name: str = Field(..., description="Person's name")
```

### Optional Field
```python
image: Optional[str] = Field(None, description="Image URL")
```

### Field with Default
```python
status: str = Field(default="pending", description="Status")
```

### Enum/Literal Field
```python
priority: Literal["high", "medium", "low"] = Field(..., description="Priority level")
```

### List Field
```python
tags: List[str] = Field(..., description="List of tags")
```

### Nested Object
```python
class Address(BaseModel):
    street: str
    city: str

class Person(BaseModel):
    name: str
    address: Address  # Nested object
```

### Dict Field
```python
metadata: Dict[str, Any] = Field(..., description="Additional metadata")
```

### Union Type (Multiple Types)
```python
cost: Union[str, int, float] = Field(..., description="Can be string or number")
```

## Accessing Structured Output

### Method 1: model_dump() (Pydantic v2)
```python
result = agent.run(prompt)
data = result.final_output.model_dump()  # Returns dict
```

### Method 2: dict() (Pydantic v1)
```python
result = agent.run(prompt)
data = result.final_output.dict()  # Returns dict
```

### Method 3: Direct Access
```python
result = agent.run(prompt)
print(result.final_output.summary)  # Access field directly
```

## Debugging Schema Issues

### Check if Field is Missing
```python
try:
    output = result.final_output.model_dump()
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Shows which fields are missing or invalid
```

### Get Schema as JSON
```python
from workflows.pydantic_schemas import VenueOutput
print(VenueOutput.model_json_schema())
```

### Validate Data Manually
```python
from workflows.pydantic_schemas import VenueOutput

data = {"summary": "...", "venues": [...]}
validated = VenueOutput(**data)  # Raises ValidationError if invalid
```

## Frontend TypeScript Types

Generate TypeScript types from Pydantic schemas:

```bash
# Install datamodel-code-generator
pip install datamodel-code-generator

# Generate TypeScript types
datamodel-codegen --input workflows/pydantic_schemas.py \
                  --output frontend/src/types/schemas.ts \
                  --output-model-type typescript
```

## Troubleshooting

### Issue: Agent returns string instead of structured output
**Solution**: Ensure ` output_type` is set on the Agent:
```python
agent = Agent(
    name="My Agent",
     output_type=MySchema,  # ← Must have this
    instructions="..."
)
```

### Issue: ValidationError on a field
**Solution**: Check field type matches schema:
```python
# Schema says Union[str, int, float]
estimated_cost: Union[str, int, float]  # OK: "$25000" or 25000

# But agent returned list
estimated_cost: ["$25000", "$30000"]  # ValidationError!
```

### Issue: Missing required field
**Solution**: Mark field as optional or provide default:
```python
# Required (will fail if missing)
name: str

# Optional (OK if missing)
name: Optional[str] = None

# With default
name: str = "Unknown"
```

### Issue: Model dump returns nested Pydantic objects
**Solution**: Use `mode='json'` for full serialization:
```python
data = result.final_output.model_dump(mode='json')
```

## Best Practices

1. **Always use descriptive field descriptions** - helps LLM understand what to generate
2. **Use Optional for truly optional fields** - required fields should always be present
3. **Provide examples in docstrings** - shows expected format
4. **Use Literal for enums** - constrains valid values
5. **Keep schemas DRY** - reuse common nested models
6. **Version your schemas** - track changes over time
7. **Test schema changes** - validate with real data before deploying

## Schema Registry

All schemas are centralized in `workflows/pydantic_schemas.py`:

```python
PYDANTIC_SCHEMAS = {
    "planning": PlanningOutput,
    "venue": VenueOutput,
    "catering": CateringOutput,
    "budgeting": BudgetingOutput,
    "programme": ProgrammeOutput,
    "speakers": SpeakersOutput,
    "activities": ActivitiesOutput,
    "entertainment": EntertainmentOutput,
    "communication": CommunicationOutput,
    "scheduling": SchedulingOutput,
    "calendar": CalendarOutput,
    "form": FormOutput,
    "logo": LogoOutput,
    "final_plan": FinalPlanOutput,
}
```

Get a schema programmatically:
```python
from workflows.pydantic_schemas import get_pydantic_schema

schema = get_pydantic_schema("venue")  # Returns VenueOutput class
```
