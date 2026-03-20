"""
New Patient Booking Flow
Complete workflow for booking an appointment as a new patient with Modmed clinic.
Includes patient registration and appointment scheduling.
"""

import random
from datetime import datetime


# Generate random patient data for each test run
def generate_patient_data():
    """Generate random patient information for testing"""
    first_names = [
        "Alex",
        "Jordan",
        "Taylor",
        "Morgan",
        "Casey",
        "Riley",
        "Jamie",
        "Avery",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Jones",
        "Brown",
        "Davis",
        "Miller",
        "Wilson",
    ]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"

    # Generate random phone number (format: XXX-XXX-XXXX)
    area_code = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    phone_number = f"{area_code}-{prefix}-{line}"
    phone_spoken = f"{area_code} {prefix} {line}"

    # Generate random email
    email = f"{first_name.lower()}.{last_name.lower()}@test.com"
    email_spoken = f"{first_name.lower()} dot {last_name.lower()} at test dot com"

    return {
        "full_name": full_name,
        "first_name": first_name,
        "phone_number": phone_number,
        "phone_spoken": phone_spoken,
        "email": email,
        "email_spoken": email_spoken,
    }


# Generate patient data once when module loads
PATIENT_DATA = generate_patient_data()

FLOW = {
    "name": "New Patient Booking - Complete Workflow",
    "phone_number": None,  # Will use TARGET_PHONE_NUMBER from .env
    "timeout": 400,  # 6-7 minutes for complete booking process
    "steps": [
        {
            "step": 1,
            "expect": "AI greeting and asking how they can help",
            "respond_with": "Say you want to book an appointment",
            "example": "I want to book an appointment",
            "assertions": [
                {"type": "step_reached", "description": "Call connected and greeted"},
                {
                    "type": "contains",
                    "value": "book",
                    "description": "Requested to book appointment",
                },
            ],
        },
        {
            "step": 2,
            "expect": "Asking if you're a new or existing patient",
            "respond_with": "Say you are a new patient",
            "example": "New patient",
            "assertions": [
                {
                    "type": "contains",
                    "value": "new",
                    "description": "Identified as new patient",
                }
            ],
        },
        {
            "step": 3,
            "expect": "Asking for your full name",
            "respond_with": f"Provide full name: {PATIENT_DATA['full_name']}",
            "example": PATIENT_DATA["full_name"],
            "assertions": [
                {
                    "type": "contains",
                    "value": PATIENT_DATA["first_name"].lower(),
                    "description": "Name provided",
                }
            ],
        },
        {
            "step": 4,
            "expect": "Asking for date of birth",
            "respond_with": "Provide date of birth: June 1, 2000",
            "example": "June first two thousand",
            "assertions": [
                {
                    "type": "contains",
                    "value": "june",
                    "description": "Date of birth provided",
                }
            ],
        },
        {
            "step": 5,
            "expect": "Asking for sex assigned at birth",
            "respond_with": "Say Male",
            "example": "Male",
            "assertions": [
                {"type": "contains", "value": "male", "description": "Sex provided"}
            ],
        },
        {
            "step": 6,
            "expect": "Asking for phone number",
            "respond_with": f"Provide phone number: {PATIENT_DATA['phone_spoken']}",
            "example": PATIENT_DATA["phone_spoken"],
            "assertions": [
                {"type": "step_reached", "description": "Phone number provided"}
            ],
        },
        {
            "step": 7,
            "expect": "Asking for email address",
            "respond_with": f"Provide email: {PATIENT_DATA['email_spoken']}",
            "example": PATIENT_DATA["email_spoken"],
            "assertions": [
                {"type": "contains", "value": "test", "description": "Email provided"}
            ],
        },
        {
            "step": 8,
            "expect": "Asking if you want to add insurance information",
            "respond_with": "Say no to skip insurance",
            "example": "No",
            "assertions": [
                {"type": "contains", "value": "no", "description": "Declined insurance"}
            ],
        },
        {
            "step": 9,
            "expect": "Checking available appointment types or asking if still there",
            "respond_with": "Confirm you're still there if asked, otherwise wait",
            "example": "Yes, I'm here",
            "assertions": [
                {"type": "step_reached", "description": "Waiting for appointment types"}
            ],
        },
        {
            "step": 10,
            "expect": "Presenting appointment type options (New Patient, Follow-up, Surgery)",
            "respond_with": "Select 'New Patient' appointment type",
            "example": "New patient",
            "assertions": [
                {
                    "type": "contains",
                    "value": "new patient",
                    "description": "Selected new patient appointment",
                }
            ],
        },
        {
            "step": 11,
            "expect": "Asking when you'd like to schedule the appointment",
            "respond_with": "Say tomorrow",
            "example": "Tomorrow",
            "assertions": [
                {
                    "type": "contains",
                    "value": "tomorrow",
                    "description": "Requested tomorrow",
                }
            ],
        },
        {
            "step": 12,
            "expect": "Presenting available time slots for tomorrow",
            "respond_with": "Select the first available option",
            "example": "Go with the first option",
            "assertions": [
                {
                    "type": "contains",
                    "value": "first",
                    "description": "Selected first time slot",
                }
            ],
        },
        {
            "step": 13,
            "expect": "Confirming appointment and asking if anything else needed",
            "respond_with": "Say thank you and that's all",
            "example": "Thank you, that's all",
            "assertions": [
                {
                    "type": "contains",
                    "value": "thank",
                    "description": "Thanked and indicated completion",
                }
            ],
        },
        {
            "step": 14,
            "expect": "Saying goodbye",
            "respond_with": "Say goodbye",
            "example": "Goodbye",
            "action": "hangup",
            "assertions": [
                {"type": "step_reached", "description": "Call completed successfully"}
            ],
        },
    ],
}

SYSTEM_PROMPT = f"""You are an AI assistant calling Modmed Test clinic to book an appointment as a NEW PATIENT.

CRITICAL RULES:
- ONLY answer the EXACT question they asked
- Do NOT volunteer additional information
- Keep responses EXTREMELY brief (1-2 sentences max, 5-10 words ideal)
- Be polite and natural
- If they say "one moment" or "checking", just wait silently
- If they ask "are you still there?", just say "Yes" or "Yes, I'm here"

PATIENT INFORMATION (use ONLY when specifically asked):
- Full Name: {PATIENT_DATA['full_name']}
- Date of Birth: June 1, 2000 (say: "June first two thousand")
- Sex: Male
- Phone: {PATIENT_DATA['phone_number']} (say: "{PATIENT_DATA['phone_spoken']}")
- Email: {PATIENT_DATA['email']} (say: "{PATIENT_DATA['email_spoken']}")
- Patient Type: NEW PATIENT
- Insurance: No (decline insurance)
- Appointment Type: New Patient
- Preferred Date: Tomorrow
- Time Preference: First available option

CONVERSATION FLOW:
1. They greet → Say "I want to book an appointment"
2. New or existing? → Say "New patient"
3. Full name? → Say "{PATIENT_DATA['full_name']}"
4. Date of birth? → Say "June first two thousand"
5. Sex? → Say "Male"
6. Phone number? → Say "{PATIENT_DATA['phone_spoken']}"
7. Email? → Say "{PATIENT_DATA['email_spoken']}"
8. Insurance? → Say "No"
9. Still there? → Say "Yes" (if asked)
10. Appointment type? → Say "New patient"
11. When? → Say "Tomorrow"
12. Which time? → Say "Go with the first option" or "First option"
13. Anything else? → Say "Thank you, that's all"
14. Goodbye → Say "Goodbye"

EXAMPLES OF CORRECT RESPONSES:
- "How can I help?" → "I want to book an appointment"
- "New or existing?" → "New patient"
- "Your name?" → "{PATIENT_DATA['full_name']}"
- "Date of birth?" → "June first two thousand"
- "Sex?" → "Male"
- "Phone number?" → "{PATIENT_DATA['phone_spoken']}"
- "Email?" → "{PATIENT_DATA['email_spoken']}"
- "Add insurance?" → "No"
- "Are you still there?" → "Yes"
- "Which appointment type?" → "New patient"
- "When would you like?" → "Tomorrow"
- "Which time slot?" → "First option"
- "Anything else?" → "Thank you, that's all"

EXAMPLES OF WRONG RESPONSES (DO NOT DO THIS):
- "Your name?" → DO NOT say "{PATIENT_DATA['full_name']}, my date of birth is..."
- "How can I help?" → DO NOT say "I want to book an appointment, I'm a new patient..."
- Just answer what they ask, nothing more!
"""

# Flow identifier (used as key in AVAILABLE_FLOWS)
FLOW_ID = "new_patient_booking"

# Print patient data for reference when flow loads
print(f"\n{'='*60}")
print(f"New Patient Booking Flow - Generated Patient Data:")
print(f"{'='*60}")
print(f"Name: {PATIENT_DATA['full_name']}")
print(f"Phone: {PATIENT_DATA['phone_number']} (say: {PATIENT_DATA['phone_spoken']})")
print(f"Email: {PATIENT_DATA['email']} (say: {PATIENT_DATA['email_spoken']})")
print(f"DOB: June 1, 2000 (say: June first two thousand)")
print(f"Sex: Male")
print(f"{'='*60}\n")
