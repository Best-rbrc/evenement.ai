# workflows/plan_generation.py
from agents import Runner, Agent, ItemHelpers
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict, List, Any
import json


async def produce_actionable_plan(coordinator: Agent, event_details: Dict[str, Any], required_agents: List[str]) -> dict:
    """
    Iterative multi-round plan generation with visible logs and handoffs.
    Each agent receives the full context (event details + prior agent outputs).
    """
    aggregated_plan = {}
    prior_output = None

    print(f"\n🧠 [LOG] Starting iterative orchestration for agents: {', '.join(required_agents)}\n")

    for round_idx, agent_name in enumerate(required_agents, start=1):
        print(f"\n🌀 [Round {round_idx}] Coordinator engaging '{agent_name.title()}' agent...\n")

        # Prepare summaries safely (outside f-strings)
        context_summary = json.dumps(aggregated_plan, indent=2) if aggregated_plan else "(no prior agent outputs yet)"
        event_json = json.dumps(event_details, indent=2)
        snippet = ""
        if prior_output:
            snippet = prior_output[:600].replace("{", "{{").replace("}", "}}")

        # Build prompt without risky nested f-strings
        input_prompt = (
            "You are continuing an event planning session for '{name}', a {etype} event.\n\n"
            "Here are the full event details as known:\n{event_json}\n\n"
            "Work with the **{agent}** specialist now to complete their section of the plan.\n\n"
            "--- PRIOR AGENT OUTPUTS ---\n{context_summary}\n\n"
            "{snippet}\n\n"
            "If there are unclear choices, either:\n"
            "  - Ask the Coordinator Agent to decide, OR\n"
            "  - Output a clear list of pending questions for the user.\n\n"
            "Output ONLY structured JSON with this agent’s section."
        ).format(
            name=event_details["event_name"],
            etype=event_details["event_type"],
            agent=agent_name,
            event_json=event_json,
            context_summary=context_summary,
            snippet=f"--- LAST ROUND SUMMARY ---\n{snippet}" if snippet else "",
        )

        # Run the streamed agent orchestration
        streamed = Runner.run_streamed(coordinator, input=input_prompt)
        round_output = ""

        async for event in streamed.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
                round_output += event.data.delta
            elif event.type == "agent_updated_stream_event":
                print(f"\n🤝 [Handoff] Agent updated: {event.new_agent.name}")
            elif event.type == "run_item_stream_event":
                if event.item.type == "message_output_item":
                    msg = ItemHelpers.text_message_output(event.item)
                    print(f"\n💬 [Message]\n{msg[:400]}...\n")

        print(f"\n✅ [LOG] Round {round_idx} ({agent_name}) complete.\n")

        # Parse JSON output
        try:
            parsed = json.loads(round_output)
        except Exception:
            parsed = {agent_name: round_output}

        aggregated_plan[agent_name] = parsed
        prior_output = round_output

    # Final synthesis
    print("\n🧩 [LOG] Coordinator synthesizing final master plan...\n")
    synthesis_context = json.dumps(aggregated_plan, indent=2)
    synthesis_prompt = (
        "You are now the overall Event Coordinator. Combine all sections into a single coherent plan for '{name}' ({etype}).\n"
        "Output valid JSON named 'final_master_plan' with unified structure, ensuring no overlaps or contradictions.\n\n"
        "Prior sections:\n{sections}"
    ).format(
        name=event_details["event_name"],
        etype=event_details["event_type"],
        sections=synthesis_context
    )

    final_run = await Runner.run(coordinator, synthesis_prompt)
    final_output = final_run.final_output

    print("\n📦 [Final Master Plan]\n", final_output[:1500], "...\n")

    return {"subplans": aggregated_plan, "master_plan": final_output}
