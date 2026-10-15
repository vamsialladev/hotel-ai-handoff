# Staff guide: Guest Request Agent

For guest-services staff. About two minutes to read. This is a simulated hotel group with synthetic guests and
bookings; **nothing is ever sent to anyone**.

**Open it:** <https://guest-request-agent.streamlit.app> (free hosting: if it says the app is asleep, click
**Yes, get this app back up** and wait about a minute).

## What it does

It reads a guest email, looks up that guest's booking (only bookings under the sender's own email address), checks
availability and the hotel's policies, and prepares:

- a **draft reply** with sources for every policy fact,
- **tasks** for the right team (front desk, housekeeping, concierge...),
- **manager actions** for anything about money or exceptions (refunds, upgrades, date changes, fee waivers). The agent
  never approves these itself.

You review everything and **Approve**, **Edit then approve**, or **Reject**.

## How to use it

1. **Inbox:** pick an email and click **Run the agent**, or write your own on **Write your own email**.
2. Read the draft, the steps the agent took, and the checks (green = passed).
3. Edit if needed, then **Approve** (it goes to the simulated outbox) or **Reject** with a reason.
4. **Outbox and tasks** shows what you approved, the task board and the manager queue.

## Things it does on purpose

- **Wrong hotel's inbox:** if a guest's booking is at the other property, the reply answers for the property they are
  actually staying at and says so.
- **Spanish emails** get a Spanish reply. If the draft comes back in the wrong language it is sent back once for a
  rewrite; if it is still wrong, the checks show it so you can fix it.
- **Escalations** (injury, safety, legal threats, harassment, press, angry refund demands) get a short holding reply
  and go to a manager. Don't add details to those replies.
- **Instructions inside an email** ("note to the system: pre-approved refund") are ignored. Never act on them.
- **If the AI is unavailable or paused**, you get a polite holding reply and a task to reply personally. No email is
  ever dropped.

## Staff sign-in (optional)

Visitors use the open **Demo mode**. With the staff password: sidebar → **Staff sign-in**. Signed in, you can
**report a draft for review** and you are not limited to 10 emails per session. You are signed out after 30 minutes
without activity.

## Please don't

- Paste real guest emails or personal details into the demo.
- Approve a reply that promises money back, an upgrade or an exception: those are for a manager.
