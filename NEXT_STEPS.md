# Next Steps for JSON Schema Validation

## ✅ Completed
- [x] Created comprehensive Pydantic schemas for all agent outputs
- [x] Updated all 14 agent files to use ` output_type` with schemas
- [x] Refactored coordinator into planning and finalization phases with appropriate schemas
- [x] Updated workflow to handle structured outputs (Pydantic models)
- [x] Simplified output parsing (removed complex regex JSON extraction)
- [x] Added proper fallbacks for edge cases
- [x] Created documentation and quick reference guide
- [x] Created test suite for schema validation

## 🔧 Testing Required

### 1. Run Unit Tests
```bash
# Install pytest if not already installed
pip install pytest

# Run schema validation tests
pytest tests/test_pydantic_schemas.py -v

# Expected: All tests should pass
```

### 2. Test Full Workflow
```bash
# Run a simple test event
python cli.py

# When prompted, enter test event details:
# - Event Name: Test Conference
# - Event Type: Conference
# - Date: 2026-06-15
# - Location: San Francisco
# - Budget: $50000-$75000
# - Guest Count: 200-300
# - Special Requirements: Tech-focused, need AV equipment
```

### 3. Verify Output Structure
Check that the workflow generates:
- ✓ Valid JSON at every phase
- ✓ All required fields present
- ✓ No JSON parsing errors in logs
- ✓ Proper field types (no strings where numbers expected)

### 4. Test Frontend Integration
```bash
# Start the backend server
python server.py

# In another terminal, start frontend
cd frontend
npm run dev

# Test:
1. Create a new event through the UI
2. Verify all agent outputs display correctly
3. Check browser console for errors
4. Verify no "Expecting value: line X" errors
```

## 🐛 Known Issues to Watch For

### Issue 1: Pydantic Version Mismatch
**Symptom**: `AttributeError: 'VenueOutput' object has no attribute 'model_dump'`
**Solution**: 
```bash
pip install --upgrade pydantic>=2.0
```

### Issue 2: OpenAI API Version
**Symptom**: ` output_type` parameter not recognized
**Solution**:
```bash
pip install --upgrade openai>=1.0.0
```

### Issue 3: Agent Returns String Instead of Structured Output
**Symptom**: Agent still returns JSON string, not Pydantic model
**Diagnostic**:
```python
# In workflow, add debug logging:
print(f"Output type: {type(result.final_output)}")
print(f"Has model_dump: {hasattr(result.final_output, 'model_dump')}")
```
**Solution**: Verify ` output_type` is set on Agent creation

## 📝 Configuration Updates Needed

### 1. Environment Variables
No new environment variables required. Existing OpenAI API key works.

### 2. Dependencies
Already in `pyproject.toml`:
```toml
[tool.poetry.dependencies]
pydantic = "^2.0.0"
openai = "^1.0.0"
```

If using pip:
```bash
pip install pydantic>=2.0.0 openai>=1.0.0
```

## 🎯 Success Criteria

### Phase 1: Planning Coordinator
- ✓ Returns valid `PlanningOutput` with all required fields
- ✓ `required_agents` list is present
- ✓ No JSON parsing errors

### Phase 2: Specialist Agents
- ✓ All agents return structured outputs matching their schemas
- ✓ venue, catering, budgeting, etc. all have valid outputs
- ✓ No validation errors in logs

### Phase 3: Finalization Coordinator
- ✓ Returns valid `FinalPlanOutput`
- ✓ Includes `timeline`, `schedule`, `budget`, `recommendations`
- ✓ All specialist outputs present in `recommendations`
- ✓ No empty objects in recommendations

### Phase 4: Output Agents
- ✓ Calendar, form, logo agents work correctly
- ✓ All outputs have correct structure

### Frontend
- ✓ No JSON parsing errors in browser console
- ✓ All event details display correctly
- ✓ Specialist recommendations show properly
- ✓ Timeline and schedule render without errors

## 🔄 Rollback Procedure

If critical issues arise:

### Step 1: Disable Structured Outputs
```python
# In each agent file, comment out  output_type:
agent = Agent(
    name="Venue Specialist",
    #  output_type=VenueOutput,  # ← Comment this
    instructions="..."
)
```

### Step 2: Revert Workflow Changes
```bash
git diff workflows/event_planning_workflow.py
# Review changes to output parsing
# Can revert to old JSON parsing if needed
```

### Step 3: Use Old Validation
Old validation code still exists in `workflows/schemas.py` and can be re-enabled.

## 📚 Documentation

- Main summary: `SCHEMA_VALIDATION_IMPLEMENTATION.md`
- Quick reference: `SCHEMA_QUICK_REFERENCE.md`
- Test suite: `tests/test_pydantic_schemas.py`
- Schema definitions: `workflows/pydantic_schemas.py`

## 🚀 Deployment Checklist

- [ ] All unit tests pass
- [ ] Full workflow test completes successfully
- [ ] Frontend displays all data correctly
- [ ] No JSON parsing errors in production logs
- [ ] Performance is acceptable (structured outputs may add 100-200ms)
- [ ] Error handling works for edge cases
- [ ] Documentation updated
- [ ] Team trained on new schema system

## 💡 Future Enhancements

1. **Schema Versioning**: Add version numbers to schemas for backward compatibility
2. **TypeScript Generation**: Auto-generate TypeScript types from Pydantic schemas
3. **Schema Registry API**: Expose schemas via API for dynamic frontend validation
4. **Schema Evolution**: Add migration system for schema changes
5. **Performance Monitoring**: Track impact of structured outputs on response time

## 📞 Support

If issues persist:
1. Check logs in `logs/workflow_*.log` for detailed error messages
2. Run test suite to isolate schema issues
3. Verify Pydantic and OpenAI library versions
4. Review schema definitions in `workflows/pydantic_schemas.py`

## ✨ Expected Benefits

Once working correctly:
- 🎯 **100% valid JSON** - no more parsing errors
- 🛡️ **Type safety** - all fields have correct types
- 🚀 **Faster debugging** - clear error messages
- 💪 **Better frontend UX** - reliable data structure
- 📈 **Easier maintenance** - single source of truth for schemas
