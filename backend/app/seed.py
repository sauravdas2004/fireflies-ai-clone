from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import ActionItem, KeyTopic, Meeting, Participant, Summary, Tag, TranscriptSegment, User


DEFAULT_USER_EMAIL = "alex.morgan@example.com"


def build_transcript(seed: list[tuple[str, float, str]]) -> list[dict[str, object]]:
    segments: list[dict[str, object]] = []
    current_start = 0.0
    for order_index, (speaker_name, duration_seconds, text) in enumerate(seed, start=1):
        end_time = round(current_start + duration_seconds, 2)
        segments.append(
            {
                "speaker_name": speaker_name,
                "start_time": round(current_start, 2),
                "end_time": end_time,
                "text": text,
                "order_index": order_index,
            }
        )
        current_start = end_time
    return segments


MEETING_FIXTURES = [
    {
        "title": "Weekly Engineering Standup",
        "days_ago": 1,
        "duration_seconds": 1860,
        "status": "completed",
        "participants": [
            {"name": "Alex Morgan", "email": "alex.morgan@example.com", "role": "Engineering Manager"},
            {"name": "Priya Shah", "email": "priya.shah@example.com", "role": "Frontend Engineer"},
            {"name": "Daniel Kim", "email": "daniel.kim@example.com", "role": "Backend Engineer"},
            {"name": "Sofia Alvarez", "email": "sofia.alvarez@example.com", "role": "Product Designer"},
        ],
        "tags": ["standup", "engineering"],
        "summary": "The team reviewed progress on the dashboard redesign, backend API stability, and the transcript search experience. Priya closed out the meeting list layout, Daniel confirmed the meeting detail endpoints are ready for mock data, and Sofia flagged a spacing issue on mobile cards. The group agreed to tighten the transcript playback sync and ship a revised draft by Friday.",
        "topics": [
            "Dashboard layout and navigation polish",
            "Transcript playback synchronization",
            "Mobile spacing fixes for meeting cards",
            "API readiness for seeded data",
        ],
        "action_items": [
            ("Priya to finish the sidebar hover states and compact card density.", "Priya Shah", False, date.today() + timedelta(days=2)),
            ("Daniel to wire the meeting detail endpoint to include summary and action items.", "Daniel Kim", False, date.today() + timedelta(days=3)),
            ("Sofia to update mobile spacing tokens in the design system.", "Sofia Alvarez", False, date.today() + timedelta(days=2)),
        ],
        "transcript": build_transcript([
            ("Alex Morgan", 42, "Quick standup. Let's start with the dashboard rewrite and what landed yesterday."),
            ("Priya Shah", 44, "I finished the meeting list card layout and added the participant avatar stack."),
            ("Daniel Kim", 48, "The detail API now returns transcript segments, summary, and action items in one payload."),
            ("Sofia Alvarez", 41, "I noticed the cards feel crowded on smaller screens. We should increase the vertical rhythm."),
            ("Priya Shah", 39, "Agreed. I can tighten the hover states and keep the active meeting highlight more obvious."),
            ("Daniel Kim", 47, "I also want to make sure transcript clicks sync the player accurately once we connect the audio placeholder."),
            ("Alex Morgan", 40, "Good. Let's use the seed data to validate the whole flow before building the frontend."),
            ("Sofia Alvarez", 44, "I will update the spacing tokens and the purple accent treatment to feel closer to Fireflies."),
            ("Priya Shah", 37, "We should keep the filters simple: title, participant, and recent first."),
            ("Daniel Kim", 43, "I'll add the search and date filters on the backend so the frontend can stay thin."),
            ("Alex Morgan", 41, "Perfect. Let's review the transcript panel interactions in the next pass."),
            ("Sofia Alvarez", 45, "The right-hand summary panel needs stronger hierarchy between overview, topics, and tasks."),
            ("Priya Shah", 38, "I'll draft the compact action item row with inline completion toggles."),
            ("Daniel Kim", 40, "I can also seed a couple of tags so we can test tag filtering later."),
            ("Alex Morgan", 39, "Ship the updated draft by Friday and we will do a full walkthrough."),
        ]),
    },
    {
        "title": "Client Check-in: Northstar Retail",
        "days_ago": 3,
        "duration_seconds": 2340,
        "status": "completed",
        "participants": [
            {"name": "Alex Morgan", "email": "alex.morgan@example.com", "role": "Account Lead"},
            {"name": "Maya Chen", "email": "maya.chen@northstar.com", "role": "Client Sponsor"},
            {"name": "Jordan Lee", "email": "jordan.lee@northstar.com", "role": "Operations Manager"},
            {"name": "Priya Shah", "email": "priya.shah@example.com", "role": "Solutions Engineer"},
        ],
        "tags": ["client-call", "account", "follow-up"],
        "summary": "Northstar Retail walked through their rollout timeline, focusing on adoption across regional teams and the reporting export workflow. The client asked for clearer action ownership, a simpler weekly summary, and a way to filter by location. Fireflies' team promised a revised onboarding outline and a sample export format before the next check-in.",
        "topics": [
            "Regional rollout timeline",
            "Weekly reporting exports",
            "Ownership for onboarding tasks",
            "Location-based filtering requests",
        ],
        "action_items": [
            ("Alex to send a revised rollout timeline with owner assignments.", "Alex Morgan", False, date.today() + timedelta(days=1)),
            ("Priya to prepare an export sample showing transcript summary and action items.", "Priya Shah", False, date.today() + timedelta(days=2)),
            ("Maya to confirm the first pilot region and user count.", "Maya Chen", False, date.today() + timedelta(days=4)),
            ("Jordan to share the current onboarding checklist with the Northstar team.", "Jordan Lee", True, date.today() + timedelta(days=1)),
        ],
        "transcript": build_transcript([
            ("Alex Morgan", 45, "Thanks for making the time. We wanted to align on rollout timing and the current blockers."),
            ("Maya Chen", 42, "We are excited, but the regional managers need a clearer weekly summary and easier exports."),
            ("Jordan Lee", 43, "The main issue is finding the right meeting notes after each call. We want the owners to be obvious."),
            ("Priya Shah", 47, "We can surface the action items more prominently and make the transcript searchable by speaker and keyword."),
            ("Alex Morgan", 41, "That would also help us during onboarding. The team wants a predictable handoff format."),
            ("Maya Chen", 40, "Can we filter by location so managers only see their own region's sessions?"),
            ("Priya Shah", 44, "Yes. For the assignment we'll use tags as the first pass, and we can later expand to richer filters."),
            ("Jordan Lee", 39, "The export should be short enough to paste into our internal update doc."),
            ("Alex Morgan", 43, "I can send a revised timeline with named owners before tomorrow morning."),
            ("Maya Chen", 38, "Great. We want the pilot to feel lightweight, not like a tool we need to babysit."),
            ("Priya Shah", 45, "We'll mock the transcript and summary screens so you can validate the workflow quickly."),
            ("Jordan Lee", 40, "Please include the due dates next to each action item if possible."),
            ("Alex Morgan", 41, "Absolutely. We'll keep the summary concise and push details into the transcript view."),
            ("Maya Chen", 44, "That should work. Let's reconvene after the first region is onboarded."),
            ("Alex Morgan", 39, "Perfect. I'll circulate the follow-up right after this call."),
            ("Priya Shah", 42, "I will also update the tag filtering mock to match your rollout structure."),
        ]),
    },
    {
        "title": "Product Planning: Q3 Fireflies Clone",
        "days_ago": 5,
        "duration_seconds": 3120,
        "status": "completed",
        "participants": [
            {"name": "Alex Morgan", "email": "alex.morgan@example.com", "role": "Product Manager"},
            {"name": "Nina Patel", "email": "nina.patel@example.com", "role": "Product Designer"},
            {"name": "Ethan Brooks", "email": "ethan.brooks@example.com", "role": "Backend Engineer"},
            {"name": "Priya Shah", "email": "priya.shah@example.com", "role": "Frontend Engineer"},
            {"name": "Liam Foster", "email": "liam.foster@example.com", "role": "QA Engineer"},
        ],
        "tags": ["planning", "product", "design-system"],
        "summary": "The group finalized the scope for the assignment implementation. They agreed to prioritize a Fireflies-like dashboard, a transcript-first meeting detail experience, and a stable SQLite-backed API. The team also discussed how to seed realistic content so the app feels usable immediately after startup.",
        "topics": [
            "Assignment scope and priorities",
            "Backend schema and persistence",
            "Realistic seed content strategy",
            "UI fidelity to the Fireflies workspace",
            "Testing and demo readiness",
        ],
        "action_items": [
            ("Ethan to finalize the normalized SQLAlchemy models and relationships.", "Ethan Brooks", False, date.today() + timedelta(days=2)),
            ("Priya to build the dashboard shell with a Fireflies-style sidebar.", "Priya Shah", False, date.today() + timedelta(days=4)),
            ("Nina to define the design tokens for spacing, color, and card elevation.", "Nina Patel", False, date.today() + timedelta(days=3)),
            ("Liam to verify the seed data covers search, filters, and completed action items.", "Liam Foster", False, date.today() + timedelta(days=5)),
        ],
        "transcript": build_transcript([
            ("Alex Morgan", 46, "We need to make the assignment feel like Fireflies, not like a generic notes app."),
            ("Nina Patel", 40, "That means the sidebar, the spacing, and the transcript panel all need to feel intentional."),
            ("Ethan Brooks", 44, "On the backend I will keep the schema normalized so the meeting detail view can hydrate in one request."),
            ("Priya Shah", 42, "I want the meeting cards to look dense but readable, with tags and participant avatars."),
            ("Liam Foster", 39, "Can we seed enough meetings to make the search and sorting meaningful on day one?"),
            ("Alex Morgan", 41, "Yes. Let's create several realistic calls so the app has variety: standups, clients, planning, and retros."),
            ("Nina Patel", 38, "The summary panel should have strong section labels for overview, topics, and tasks."),
            ("Ethan Brooks", 45, "I will use cascading deletes so if a meeting is removed, the children disappear cleanly."),
            ("Priya Shah", 43, "We should also think about tag filtering because it adds a lot of value with minimal UI complexity."),
            ("Liam Foster", 40, "I'll test the action item states and confirm completed items render differently."),
            ("Alex Morgan", 39, "Good. The seed script needs to read like real conversations, not placeholder text."),
            ("Ethan Brooks", 44, "I can keep the timestamps monotonic so the transcript binary search later is straightforward."),
            ("Nina Patel", 41, "The user should be able to scan the transcript and summary without feeling lost."),
            ("Priya Shah", 42, "Agreed. I'll keep the interaction model close to the original product."),
            ("Liam Foster", 38, "Once the models are ready, I can validate the seed counts and the foreign key relationships."),
            ("Alex Morgan", 40, "Let's lock this phase and move into the API only after the schema is stable."),
            ("Nina Patel", 37, "That gives us a clean foundation for the frontend."),
        ]),
    },
    {
        "title": "Marketing Sync: Launch Messaging",
        "days_ago": 8,
        "duration_seconds": 1980,
        "status": "completed",
        "participants": [
            {"name": "Alex Morgan", "email": "alex.morgan@example.com", "role": "Product Marketing"},
            {"name": "Grace Hall", "email": "grace.hall@example.com", "role": "Content Lead"},
            {"name": "Owen Reed", "email": "owen.reed@example.com", "role": "Demand Gen"},
            {"name": "Priya Shah", "email": "priya.shah@example.com", "role": "Frontend Engineer"},
        ],
        "tags": ["marketing", "launch", "copy"],
        "summary": "Marketing aligned on launch messaging for the clone demo, emphasizing productivity, search, and transcript clarity. The team discussed a short headline for the home page, supporting proof points, and the need to show the product in action within a few seconds. They also agreed to avoid over-explaining the mock AI pieces and keep the experience crisp.",
        "topics": [
            "Launch headline and positioning",
            "Demo flow and first impression",
            "Proof points for productivity claims",
            "Copy for mocked AI features",
        ],
        "action_items": [
            ("Grace to draft the homepage headline and short supporting copy.", "Grace Hall", False, date.today() + timedelta(days=2)),
            ("Owen to define the demo path that shows transcript search in under 20 seconds.", "Owen Reed", False, date.today() + timedelta(days=3)),
            ("Priya to make sure the meeting list and detail pages load with strong empty states.", "Priya Shah", False, date.today() + timedelta(days=4)),
        ],
        "transcript": build_transcript([
            ("Alex Morgan", 41, "We need the demo to feel immediate. People should understand the product in the first few seconds."),
            ("Grace Hall", 44, "That means the homepage copy has to be crisp and the product promise needs to be obvious."),
            ("Owen Reed", 39, "I want the walkthrough to jump straight into a real meeting record with a transcript and summary."),
            ("Priya Shah", 46, "I can preload the seed meetings so the dashboard never feels empty."),
            ("Alex Morgan", 40, "Good. We should lean into the productivity angle and the meeting search workflow."),
            ("Grace Hall", 38, "Can we mention notes, tasks, and summaries without sounding overloaded?"),
            ("Priya Shah", 42, "Yes. The UI should present those as tabs or sections with clear visual hierarchy."),
            ("Owen Reed", 41, "For the demo, the transcript search highlight is the most impressive interaction."),
            ("Alex Morgan", 39, "Let's keep the AI language modest since the summaries are seeded or mocked."),
            ("Grace Hall", 43, "That actually helps. We can focus on what the product does for the user rather than how it works."),
            ("Priya Shah", 40, "I'll make sure the Fireflies-style purple accent is present but not overwhelming."),
            ("Owen Reed", 37, "The landing state should move people from curiosity to action quickly."),
            ("Alex Morgan", 42, "Exactly. We are selling workflow clarity, not a feature list."),
            ("Grace Hall", 41, "Then let's keep the copy short and the UI polished."),
            ("Priya Shah", 38, "I will align the spacing and card rhythm with that direction."),
        ]),
    },
    {
        "title": "Retro: Sprint 12 Demo Review",
        "days_ago": 11,
        "duration_seconds": 2220,
        "status": "completed",
        "participants": [
            {"name": "Alex Morgan", "email": "alex.morgan@example.com", "role": "Facilitator"},
            {"name": "Mina Brooks", "email": "mina.brooks@example.com", "role": "Engineer"},
            {"name": "Noah Diaz", "email": "noah.diaz@example.com", "role": "Engineer"},
            {"name": "Priya Shah", "email": "priya.shah@example.com", "role": "Frontend Engineer"},
        ],
        "tags": ["retro", "feedback", "engineering"],
        "summary": "The team reviewed the last demo and identified areas to simplify the navigation, improve transcript readability, and reduce visual noise. They agreed that the best path was to create a more obvious active meeting state and tighter spacing between transcript rows. The retro closed with a commitment to keep the next iteration narrower and more polished.",
        "topics": [
            "Demo feedback and visual noise",
            "Active meeting state clarity",
            "Transcript row spacing",
            "Prioritization for the next iteration",
        ],
        "action_items": [
            ("Priya to simplify the transcript row typography and spacing.", "Priya Shah", False, date.today() + timedelta(days=2)),
            ("Mina to test the active state treatment for the selected meeting in the sidebar.", "Mina Brooks", False, date.today() + timedelta(days=3)),
            ("Noah to review the summary panel collapse behavior on smaller screens.", "Noah Diaz", False, date.today() + timedelta(days=3)),
        ],
        "transcript": build_transcript([
            ("Alex Morgan", 43, "Let's review what worked in the demo and what felt noisy."),
            ("Mina Brooks", 41, "The core flow is solid, but the navigation could be clearer when the list gets long."),
            ("Noah Diaz", 39, "I also noticed the transcript rows need more breathing room so the speaker labels stand out."),
            ("Priya Shah", 44, "I can tighten the hierarchy by reducing the secondary text weight and spacing the timestamps better."),
            ("Alex Morgan", 40, "The active meeting state should be visible at a glance."),
            ("Mina Brooks", 38, "A stronger left border or background tint would help a lot."),
            ("Noah Diaz", 42, "The summary panel is useful, but we should avoid packing too much into the first view."),
            ("Priya Shah", 40, "I will keep the overview concise and push the detail into collapsible sections."),
            ("Alex Morgan", 39, "We should not make people hunt for the transcript search box."),
            ("Mina Brooks", 37, "Agreed. It belongs in the panel header with strong contrast."),
            ("Noah Diaz", 43, "The action items should feel like tasks, not just more body copy."),
            ("Priya Shah", 41, "I can add checkboxes and a clearer completed state."),
            ("Alex Morgan", 38, "Great. Let's narrow the next iteration to readability and workflow clarity."),
            ("Mina Brooks", 40, "That will make the app feel much closer to the product we're referencing."),
            ("Noah Diaz", 39, "Once those refinements land, the experience should feel much more premium."),
        ]),
    },
    {
        "title": "Customer Success Handoff",
        "days_ago": 13,
        "duration_seconds": 2100,
        "status": "completed",
        "participants": [
            {"name": "Alex Morgan", "email": "alex.morgan@example.com", "role": "Customer Success"},
            {"name": "Iris Cooper", "email": "iris.cooper@example.com", "role": "CSM"},
            {"name": "Ben Turner", "email": "ben.turner@example.com", "role": "Implementation Manager"},
            {"name": "Priya Shah", "email": "priya.shah@example.com", "role": "Frontend Engineer"},
        ],
        "tags": ["customer-success", "handoff", "planning"],
        "summary": "Customer success reviewed the handoff process for new accounts and agreed that the meeting detail view should make follow-up tasks, transcript context, and participant ownership easy to scan. The team wants a consistent way to carry notes from kickoff into onboarding without losing the thread between calls.",
        "topics": [
            "Handoff workflow between teams",
            "Participant ownership clarity",
            "Keeping context across meetings",
            "Follow-up task visibility",
        ],
        "action_items": [
            ("Iris to draft a standard handoff checklist for new accounts.", "Iris Cooper", False, date.today() + timedelta(days=3)),
            ("Ben to map onboarding milestones into the next meeting template.", "Ben Turner", False, date.today() + timedelta(days=4)),
            ("Priya to ensure the meeting detail view surfaces owner names clearly.", "Priya Shah", False, date.today() + timedelta(days=2)),
        ],
        "transcript": build_transcript([
            ("Alex Morgan", 42, "We need the handoff from sales to customer success to feel seamless for every new account."),
            ("Iris Cooper", 39, "The biggest pain point is losing context between the kickoff and the first onboarding call."),
            ("Ben Turner", 41, "If the transcript summary keeps the key decisions upfront, the team can move faster."),
            ("Priya Shah", 38, "The meeting detail page should make the action items and owners obvious at a glance."),
            ("Alex Morgan", 40, "That also helps with follow-up because people can check the work directly in the app."),
            ("Iris Cooper", 37, "I would like a checklist that captures who owns setup, training, and data validation."),
            ("Ben Turner", 43, "We can map that into the seed data so the workflow is easy to demo."),
            ("Priya Shah", 36, "I will keep the summary layout consistent with the other meeting types."),
            ("Alex Morgan", 39, "The idea is to keep the handoff visible without making the page feel heavy."),
            ("Iris Cooper", 41, "That should work well if the tags clearly distinguish customer success sessions."),
            ("Ben Turner", 35, "We can also use this meeting type to test the participant filter later."),
            ("Priya Shah", 38, "And it gives us one more realistic dataset for the transcript search experience."),
            ("Alex Morgan", 40, "Perfect, let's include it in the seed set so the app has more variety."),
            ("Iris Cooper", 34, "I will draft the checklist after this call."),
            ("Ben Turner", 33, "I will update the onboarding template this week."),
        ]),
    },
]


def get_or_create_user(session) -> User:
    user = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    if user:
        return user

    user = User(
        name="Alex Morgan",
        email=DEFAULT_USER_EMAIL,
        avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=128&q=80",
    )
    session.add(user)
    session.flush()
    return user


def get_or_create_tag(session, tag_name: str) -> Tag:
    tag = session.scalar(select(Tag).where(Tag.name == tag_name))
    if tag:
        return tag

    tag = Tag(name=tag_name)
    session.add(tag)
    session.flush()
    return tag


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        existing_meetings = session.scalar(select(Meeting.id))
        if existing_meetings is not None:
            print("Seed skipped: meetings already exist.")
            return

        user = get_or_create_user(session)

        for fixture in MEETING_FIXTURES:
            meeting = Meeting(
                title=fixture["title"],
                date=datetime.now(timezone.utc) - timedelta(days=fixture["days_ago"]),
                duration_seconds=fixture["duration_seconds"],
                created_by=user.id,
                audio_url=f"https://example.com/audio/{fixture['title'].lower().replace(' ', '-')}.mp3",
                status=fixture["status"],
            )
            session.add(meeting)
            session.flush()

            for participant_data in fixture["participants"]:
                session.add(
                    Participant(
                        meeting_id=meeting.id,
                        name=participant_data["name"],
                        email=participant_data["email"],
                        role=participant_data["role"],
                    )
                )

            for segment in fixture["transcript"]:
                session.add(TranscriptSegment(meeting_id=meeting.id, **segment))

            session.add(
                Summary(
                    meeting_id=meeting.id,
                    overview_text=fixture["summary"],
                    generated_at=datetime.now(timezone.utc),
                )
            )

            for order_index, topic_text in enumerate(fixture["topics"], start=1):
                session.add(
                    KeyTopic(
                        meeting_id=meeting.id,
                        topic_text=topic_text,
                        order_index=order_index,
                    )
                )

            for text, assignee, is_completed, due_date in fixture["action_items"]:
                session.add(
                    ActionItem(
                        meeting_id=meeting.id,
                        text=text,
                        assignee=assignee,
                        is_completed=is_completed,
                        due_date=due_date,
                    )
                )

            for tag_name in fixture["tags"]:
                meeting.tags.append(get_or_create_tag(session, tag_name))

        session.commit()
        print(f"Seeded {len(MEETING_FIXTURES)} meetings with realistic transcript data.")


if __name__ == "__main__":
    seed_database()
