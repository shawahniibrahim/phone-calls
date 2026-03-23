# Tampa Heart Test Cases

Derived from CaesarHealth Linear tickets created by `i.shawahni@bitlab.co`.

## TH-001 - Continue to slot search after patient creation

Ticket: [CAE-329](https://linear.app/bitlab-workspace/issue/CAE-329)

Preconditions:
- Tampa Heart booking flow is active.
- A caller can complete the patient creation path.
- A valid provider or provider preference is available.

Steps:
1. Call the Tampa Heart line to book an appointment.
2. Complete the steps needed for the system to create or locate the patient record.
3. Choose a provider or continue with the next booking step.
4. Ask to proceed with scheduling.

Expected result:
- After the patient record is set, the agent moves into availability lookup.
- The agent does not stall after patient creation.
- The agent offers slots or asks the next required scheduling question.

## TH-002 - Insurance scheduling restriction persists during reschedule

Ticket: [CAE-328](https://linear.app/bitlab-workspace/issue/CAE-328)

Preconditions:
- Tampa Heart booking flow supports insurance-based appointments.
- An insurance-based appointment is booked more than one week in the future.

Steps:
1. Book an appointment as a patient using insurance.
2. Accept a slot that is at least one week in the future.
3. End the call and call back to reschedule that same appointment.
4. Request an earlier date that violates the insurance timing rule.

Expected result:
- The agent recognizes the appointment as insurance-based during reschedule.
- The original one-week restriction still applies.
- The agent refuses or reroutes the reschedule request instead of moving it to an invalid earlier date.

## TH-003 - No provider preference is accepted

Ticket: [CAE-327](https://linear.app/bitlab-workspace/issue/CAE-327)

Preconditions:
- Tampa Heart booking flow is active.
- The patient profile does not require a specific provider.

Steps:
1. Call to book an appointment.
2. Reach the step where the agent asks which provider you want.
3. Say that you have no preference or ask for the next available provider.

Expected result:
- The agent accepts "no preference" as a valid answer.
- The agent does not loop on the provider selection question.
- The agent continues to the next available provider and slot search flow.

## TH-004 - Appointment type is not mistaken for a physician

Ticket: [CAE-326](https://linear.app/bitlab-workspace/issue/CAE-326)

Preconditions:
- Tampa Heart has appointment types such as ultrasound available in the flow.
- Provider names are configured separately from appointment types.

Steps:
1. Call the Tampa Heart line and begin scheduling.
2. Ask for an ultrasound or select ultrasound when discussing appointment type.
3. Continue through provider and slot lookup.

Expected result:
- The agent treats ultrasound as an appointment type, not as a physician name.
- The agent does not search for appointments under a fake provider named ultrasound.
- Provider lookup and spoken confirmations remain accurate.
