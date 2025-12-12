# Schema Validation Migration Checklist

## Pre-Deployment Verification

### Dependencies ✓
```bash
# Verify Python version (3.8+)
python --version

# Check installed packages
pip list | grep pydantic
pip list | grep openai

# Should see:
# pydantic >= 2.0.0
# openai >= 1.0.0
```

### Code Changes ✓
```bash
# Verify all files were updated
git status

# Expected changes:
# Modified: 16 files
# New: 4 files (schemas, tests, docs)
```

### Test Execution ✓
```bash
# Run schema validation tests
pytest tests/test_pydantic_schemas.py -v

# All tests should PASS
# If any fail, review error messages
```

## Deployment Steps

### 1. Backup Current System
```bash
# Create backup branch
git checkout -b backup-before-schema-validation
git push origin backup-before-schema-validation

# Return to main branch
git checkout main
```

### 2. Deploy New Code
```bash
# Merge schema validation changes
git add -A
git commit -m "feat: implement JSON schema validation with Pydantic"
git push origin main
```

### 3. Update Environment
```bash
# Install/update dependencies
pip install --upgrade pydantic>=2.0.0 openai>=1.0.0

# Or with poetry
poetry install
poetry update pydantic openai
```

### 4. Restart Services
```bash
# Stop existing services
pkill -f "python server.py"
pkill -f "npm run dev"

# Start backend
python server.py &

# Start frontend (in separate terminal)
cd frontend && npm run dev &
```

## Post-Deployment Testing

### Test 1: Basic Workflow ✓
```bash
# Run CLI test
python cli.py

# Enter test data:
Event Name: Test Event
Event Type: Workshop
Date: 2026-07-15
Location: New York
Budget: $25000-$50000
Guests: 50-100
Requirements: Interactive sessions

# Verify: No JSON errors in output
```

### Test 2: Check Logs ✓
```bash
# Find latest log file
ls -lt logs/workflow_*.log | head -1

# Check for errors
grep -i "error\|fail\|invalid" logs/workflow_*.log

# Should see: "validation: SUCCESS (structured output)"
```

### Test 3: Frontend Integration ✓
1. Open browser to http://localhost:5173
2. Create new event via voice or form
3. Verify all sections load correctly
4. Check browser console (F12) - no errors
5. Verify event details display properly

### Test 4: API Endpoints ✓
```bash
# Test voice-to-form endpoint
curl -X POST http://localhost:8000/api/voice-to-form \
  -H "Content-Type: application/json" \
  -d '{"transcript":"Plan a tech conference in San Francisco for 200 people in June 2026"}'

# Should return valid JSON with event_name, event_type, etc.
```

## Monitoring

### What to Watch
1. **Response Times**: Structured outputs may add 100-200ms
2. **Error Rates**: Should decrease (no more JSON parsing errors)
3. **Log Messages**: Look for "structured output" success messages
4. **Frontend Errors**: Monitor browser console for schema issues

### Key Metrics
- JSON parsing errors: Should be **0**
- Schema validation failures: Should be **< 1%**
- Average response time: Should be **< 5 seconds per agent**
- Frontend errors: Should be **< 1%**

## Troubleshooting Guide

### Problem: "AttributeError: 'Agent' object has no attribute ' output_type'"
**Cause**: Old OpenAI Agents SDK version
**Fix**:
```bash
pip install --upgrade openai
# Restart server
```

### Problem: "ValidationError: Field required"
**Cause**: Agent not returning all required fields
**Fix**: Check schema definition, make field Optional if truly optional
```python
# In pydantic_schemas.py
field: Optional[str] = None  # Not field: str
```

### Problem: Agent still returns JSON string
**Cause**:  output_type not properly set
**Fix**: Verify agent creation:
```python
# Check in agent file
agent = Agent(
    name="...",
     output_type=MySchema,  # ← Must be present
    instructions="..."
)
```

### Problem: Frontend shows "undefined" for fields
**Cause**: Frontend TypeScript types don't match Pydantic schemas
**Fix**: Update frontend types or generate from schemas:
```bash
# Generate TypeScript types
pip install datamodel-code-generator
datamodel-codegen --input workflows/pydantic_schemas.py \
                  --output frontend/src/types/schemas.ts \
                  --output-model-type typescript
```

### Problem: "model_dump() not found"
**Cause**: Pydantic v1 installed instead of v2
**Fix**:
```bash
pip install --upgrade 'pydantic>=2.0.0'
```

## Rollback Procedure

If major issues occur:

### Quick Rollback (Disable Structured Outputs)
```bash
# Find all  output_type lines
grep -r " output_type=" custom_agents/

# Comment them out temporarily
# This disables structured outputs but keeps other changes
```

### Full Rollback
```bash
# Switch to backup branch
git checkout backup-before-schema-validation

# Restart services
# ... (same as deployment steps)
```

## Success Indicators

✅ All agents return structured outputs  
✅ No JSON parsing errors in logs  
✅ Frontend displays all data correctly  
✅ Response times acceptable (< 5s per agent)  
✅ Error rates low (< 1%)  
✅ Team comfortable with new system  

## Team Communication

### Announce to Team
```
📢 Schema Validation System Deployed

What changed:
- All agents now return validated JSON (Pydantic schemas)
- No more JSON parsing errors
- Better type safety and error messages

What to watch:
- Monitor logs for any validation errors
- Report any frontend display issues
- Note if response times increase significantly

Docs:
- Implementation: SCHEMA_VALIDATION_IMPLEMENTATION.md
- Quick Reference: SCHEMA_QUICK_REFERENCE.md
- Next Steps: NEXT_STEPS.md
```

## Training Materials

### For Developers
1. Read `SCHEMA_QUICK_REFERENCE.md`
2. Review `workflows/pydantic_schemas.py`
3. Practice adding/modifying a field in a schema
4. Run test suite to verify changes

### For QA
1. Focus on testing all agent outputs
2. Verify frontend displays correctly
3. Check for JSON errors in browser console
4. Report any "undefined" or missing fields

## Sign-Off

- [ ] Pre-deployment tests passed
- [ ] Code deployed successfully
- [ ] Services restarted
- [ ] Post-deployment tests passed
- [ ] Monitoring in place
- [ ] Team notified
- [ ] Documentation complete

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Approved By**: _______________  

## Contact

Issues or questions:
- Check docs: `SCHEMA_*.md` files
- Review tests: `tests/test_pydantic_schemas.py`
- Check logs: `logs/workflow_*.log`
