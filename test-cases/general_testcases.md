# General Test Cases

Derived from CaesarHealth Linear tickets created by `i.shawahni@bitlab.co`.

Use these for cases that are not tied to a single clinic file. Each test case includes a scope line so ModMed-only or platform-only coverage stays easy to filter later.

## Conversation Flow

### GEN-001 - Provider and appointment reason are collected before recap

Ticket: [CAE-110](https://linear.app/bitlab-workspace/issue/CAE-110)  
Scope: General phone flow

Preconditions:
- Booking flow is active.

Steps:
1. Call to book an appointment.
2. Provide enough information to reach the booking summary step.
3. Do not volunteer provider preference or appointment reason unless asked.

Expected result:
- The agent explicitly asks for provider preference when required.
- The agent explicitly asks for appointment reason when required.
- The final recap does not claim provider or reason were unspecified unless the caller actually said so.

### GEN-002 - Data confirmation is not overly repetitive

Ticket: [CAE-105](https://linear.app/bitlab-workspace/issue/CAE-105)  
Scope: General phone flow

Preconditions:
- Any booking, reschedule, or cancel flow is active.

Steps:
1. Call the agent and complete a normal appointment-related task.
2. Observe how often the agent repeats the collected data back to the caller.

Expected result:
- The agent confirms data at sensible checkpoints instead of after every small answer.
- Repeated confirmations do not interrupt flow progress.
- The caller hears a single clear recap before a committed action when needed.

### GEN-003 - Refusing consent ends the flow respectfully

Ticket: [CAE-106](https://linear.app/bitlab-workspace/issue/CAE-106)  
Scope: General phone flow

Preconditions:
- The agent requests consent before collecting personal information.

Steps:
1. Start a call and trigger the consent prompt.
2. Refuse consent to information collection.

Expected result:
- The agent does not continue collecting personal details.
- The agent explains it cannot proceed without consent.
- The call ends or reroutes according to policy without trying to bypass the refusal.

### GEN-004 - Consent changed from no to yes still triggers confirmation

Ticket: [CAE-107](https://linear.app/bitlab-workspace/issue/CAE-107)  
Scope: General phone flow

Preconditions:
- The agent asks for consent before collecting personal information.

Steps:
1. Begin a call and initially refuse consent.
2. Change your mind and ask to continue.
3. Provide the requested information.

Expected result:
- The agent resumes the normal collection path once consent is granted.
- The agent confirms the collected information before taking action.
- The flow does not skip confirmation because consent was first refused.

### GEN-005 - The call does not restart after a closing thank you

Ticket: [CAE-108](https://linear.app/bitlab-workspace/issue/CAE-108)  
Scope: General phone flow

Preconditions:
- Complete any supported flow until the conversation is effectively finished.

Steps:
1. Reach the end of a successful call.
2. Say "thank you" or another natural closing phrase.

Expected result:
- The agent closes the conversation.
- The agent does not replay the opening greeting or restart the workflow.
- The call can end cleanly.

### GEN-006 - Post-submission guidance uses the approved wording

Ticket: [CAE-109](https://linear.app/bitlab-workspace/issue/CAE-109)  
Scope: General phone flow

Preconditions:
- A booking or request-submission flow reaches the "what happens next" explanation.

Steps:
1. Submit an appointment request through the call flow.
2. Listen to the guidance the agent gives after submission.

Expected result:
- The agent uses the updated wording pattern based on "First," "Then," and "Lastly."
- The spoken guidance sounds natural and patient-friendly.
- The sequence of next steps remains correct.

### GEN-007 - Cancel flow does not promise transfer and then self-submit

Ticket: [CAE-104](https://linear.app/bitlab-workspace/issue/CAE-104)  
Scope: General phone flow

Preconditions:
- The agent supports canceling an existing appointment.

Steps:
1. Call to cancel an appointment.
2. Follow the flow until the agent explains how it will complete the request.

Expected result:
- The agent describes the actual next action truthfully.
- If the system will submit the cancellation itself, it does not say it is transferring to a scheduling team.
- The spoken path and the executed path match.

### GEN-008 - Greeting uses the public assistant identity, not an internal Retell name

Ticket: [CAE-157](https://linear.app/bitlab-workspace/issue/CAE-157)  
Scope: ModMed

Preconditions:
- A ModMed-backed agent is live.

Steps:
1. Start a new call and listen to the greeting.

Expected result:
- The greeting uses the intended clinic or assistant name.
- Internal Retell-facing names and technical identifiers are never spoken to the caller.

### GEN-009 - Gender confirmation uses a neutral tone

Ticket: [CAE-158](https://linear.app/bitlab-workspace/issue/CAE-158)  
Scope: ModMed

Preconditions:
- New-patient or identity collection flow includes sex or gender collection.

Steps:
1. Start a call that reaches the sex or gender question.
2. Answer the question and listen to the confirmation line.

Expected result:
- The confirmation line is neutral and professional.
- The tone does not sound celebratory, judgmental, or awkward.

### GEN-010 - Appointment type recognition accepts natural phrasing

Ticket: [CAE-155](https://linear.app/bitlab-workspace/issue/CAE-155)  
Scope: ModMed

Preconditions:
- The flow includes appointment type selection.

Steps:
1. Reach the appointment type prompt.
2. Say "follow up" without adding the word "appointment."

Expected result:
- The agent recognizes "follow up" as the intended appointment type.
- The agent does not mishear it as unrelated wording.
- The flow continues without forcing the caller to restate the phrase unnaturally.

### GEN-011 - Confirm appointment intent never loops indefinitely

Ticket: [CAE-162](https://linear.app/bitlab-workspace/issue/CAE-162)  
Scope: ModMed

Preconditions:
- A patient has an existing appointment that could be confirmed, or the product intentionally does not support confirmation.

Steps:
1. Call the ModMed-backed line.
2. Ask to confirm an appointment.

Expected result:
- The agent either completes a supported confirmation flow or clearly states confirmation is not supported.
- The agent offers valid alternatives such as booking, rescheduling, or canceling when needed.
- The conversation does not enter an infinite loop.

### GEN-012 - Reschedule changes the existing appointment instead of creating a second one

Ticket: [CAE-163](https://linear.app/bitlab-workspace/issue/CAE-163)  
Scope: ModMed

Preconditions:
- A patient has exactly one upcoming appointment.

Steps:
1. Call to reschedule the upcoming appointment.
2. Choose a new valid slot and complete the flow.
3. Review the patient's appointment list after the call.

Expected result:
- The original appointment is replaced or updated.
- The patient is not left with both the old and the new appointment active.
- Cancel and list-appointments flows reflect the rescheduled slot correctly.

### GEN-013 - Relative day and date requests are interpreted correctly

Ticket: [CAE-161](https://linear.app/bitlab-workspace/issue/CAE-161)  
Scope: ModMed

Preconditions:
- The agent can search for appointments by date or weekday.

Steps:
1. Ask for an appointment using a relative weekday such as "next Monday."
2. If nothing is available, ask for a different relative day such as "next Saturday."
3. Choose a returned slot and listen to the confirmation.

Expected result:
- The agent correctly interprets each requested day.
- The confirmed appointment matches the day and date the caller chose.
- The agent does not drift to a different date because of earlier search context.

### GEN-014 - Reschedule flow skips unnecessary new/existing branching

Ticket: [CAE-154](https://linear.app/bitlab-workspace/issue/CAE-154)  
Scope: ModMed

Preconditions:
- A patient has an appointment eligible for reschedule.

Steps:
1. Call and ask to reschedule an appointment.
2. Follow the flow from identification through appointment selection.

Expected result:
- The agent does not ask whether the caller is new or existing once reschedule intent is clear.
- After the patient is found, the agent presents the caller's current appointment choices first.
- The agent then continues with reschedule-specific slot selection.

### GEN-015 - New-patient data collection happens in manageable turns

Ticket: [CAE-182](https://linear.app/bitlab-workspace/issue/CAE-182)  
Scope: ModMed

Preconditions:
- New-patient booking flow is active.

Steps:
1. Start a call as a new patient booking an appointment.
2. Observe how the agent asks for registration details.

Expected result:
- The agent collects required details in manageable turns.
- The agent does not ask for an overwhelming block of details all at once.

### GEN-016 - Phone number is repeated back clearly for confirmation

Ticket: [CAE-182](https://linear.app/bitlab-workspace/issue/CAE-182)  
Scope: ModMed

Preconditions:
- A flow includes phone number capture.

Steps:
1. Provide a phone number during the call.
2. Listen to the confirmation step.

Expected result:
- The agent repeats the captured phone number back to the caller.
- The repeated number is spoken clearly enough to verify accuracy.

### GEN-017 - Announced slot count matches the slots the caller hears

Ticket: [CAE-182](https://linear.app/bitlab-workspace/issue/CAE-182)  
Scope: ModMed

Preconditions:
- The system can return multiple appointment slots.

Steps:
1. Search for availability on a date with many returned slots.
2. Listen to the count the agent announces and the list it reads back.

Expected result:
- The spoken slot count matches the slots actually presented.
- If the agent intentionally presents only a subset, it says so explicitly.

### GEN-018 - Offered appointment times are spoken in chronological order

Ticket: [CAE-182](https://linear.app/bitlab-workspace/issue/CAE-182)  
Scope: ModMed

Preconditions:
- Multiple appointment slots exist on the same date.

Steps:
1. Ask for availability on a date with several open times.
2. Listen to the order in which the times are presented.

Expected result:
- The agent announces the appointment times in chronological order.
- Later times are not read before earlier times on the same date.

## Data Integrity

### GEN-019 - Captured sex is persisted in session or EMR data

Ticket: [CAE-159](https://linear.app/bitlab-workspace/issue/CAE-159)  
Scope: ModMed

Preconditions:
- New-patient flow collects sex or gender.

Steps:
1. Complete a new-patient flow and provide sex or gender when asked.
2. Review the resulting session data or EMR payload.

Expected result:
- The captured sex or gender is present in the resulting data.
- The persisted value matches what the caller said.

### GEN-020 - Patient records do not default to Unknown gender unexpectedly

Ticket: [CAE-115](https://linear.app/bitlab-workspace/issue/CAE-115)  
Scope: Platform or patient creation flow

Preconditions:
- A new patient can be created through the relevant workflow.

Steps:
1. Create a new patient record through the supported flow.
2. Review the stored patient details afterward.

Expected result:
- Gender handling is explicit and consistent.
- The workflow does not silently create a patient with `Unknown` gender unless that is the intended fallback.
- If gender is required, the system collects or surfaces it clearly.

## Access And Security

### GEN-021 - HCP profile cannot access call details by direct URL

Ticket: [CAE-160](https://linear.app/bitlab-workspace/issue/CAE-160)  
Scope: Platform access control

Preconditions:
- At least one call record exists.
- A user can switch between clinic operations and HCP roles.

Steps:
1. Open a call details page while using a role that is allowed to view it.
2. Copy the direct URL.
3. Switch to an HCP profile.
4. Open the copied URL directly.

Expected result:
- The HCP profile is blocked from viewing the call details.
- Direct-link access does not bypass UI-level permissions.
