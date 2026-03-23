# Experience Dermatology Test Cases

Derived from CaesarHealth Linear tickets created by `i.shawahni@bitlab.co`.

## ED-001 - Cancellation sends SMS confirmation

Ticket: [CAE-325](https://linear.app/bitlab-workspace/issue/CAE-325)

Preconditions:
- Experience Dermatology cancellation flow is active.
- SMS notifications are enabled for appointment events.
- The patient has a cancelable appointment and a valid mobile number on file.

Steps:
1. Call the Experience Dermatology line.
2. Cancel an existing appointment successfully.
3. End the call and monitor the patient phone number for the post-call notification.

Expected result:
- The appointment is canceled successfully.
- A cancellation SMS is sent to the patient.
- The cancellation SMS content matches the clinic's expected template and references the canceled appointment.
