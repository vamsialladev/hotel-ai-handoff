# Staff guide: Hotel Operations Knowledge Assistant

For front-desk staff. About two minutes to read. This is a simulated hotel group with synthetic documents.

**Open it:** <https://hotel-ops-assistant.streamlit.app> (free hosting: if it says the app is asleep, click
**Yes, get this app back up** and wait about a minute).

## What it does

You type a question about the hotel's policies, fees, amenities or procedures. It answers in a few sentences from the
hotel's own documents and shows where each fact came from (numbered sources you can open). It never makes bookings
and never looks up guests.

## How to ask

1. Pick your property at the top (**Beach Resort** or **Mountain Lodge**).
2. Ask one thing at a time, the way a guest would: *"Can a guest bring their dog?"*, *"How late can a Gold member check
   out on Saturday?"*
3. Spanish works too: *"¿Cuánto cuesta el estacionamiento?"* gets a Spanish answer from the English documents.
4. Read the answer and the source under it. If the answer matters (money, rules), open the source.

## When it says no

- **"I couldn't find this in the hotel's documents. Please check with a manager."** The documents don't cover it. It
  will not guess. Ask your manager.
- **A yellow "Check with a manager" note:** the documents say a manager must decide (refunds over the front-desk limit,
  non-refundable rates, repeated noise complaints).
- **"This sounds like an emergency..."** Anything about fire, smoke, gas, injuries or someone unresponsive gets this
  message immediately. Follow the hotel's posted emergency procedures, call 911 if anyone may be in danger, and
  contact the Manager on Duty. The assistant has no emergency procedure it can read.
- **"Answers are paused for a moment..."** The owner has paused the assistant. Use the documents or ask a manager.

## Staff sign-in (optional)

Visitors use the open **Demo mode**. If your manager gave you the staff password: sidebar → **Staff sign-in**.
Signed in, you can **report an answer for review** (sidebar → *Report an answer for review*: pick the question, a
reason and an optional note) and you are not limited to 20 questions per session. You are signed out after 30 minutes
without activity. Never share the staff password or write it on a note at the desk.

## Please don't

- Type a guest's personal details (names, phone numbers, emails, card numbers). They are removed before anything is
  stored, but the safest data is data never typed.
- Treat an answer as permission for a refund or exception: those always need a manager.
