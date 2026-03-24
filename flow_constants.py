from enum import StrEnum


class ASSERTIONS(StrEnum):
    STEP_REACHED = "step_reached"
    CONTAINS = "contains"
    CONTAINS_ANY = "contains_any"
    NOT_CONTAINS = "not_contains"
    MATCHES = "matches"


class TARGETS(StrEnum):
    EITHER = "either"
    CLINIC = "clinic"
    OURS = "ours"


class ASSERT_ON(StrEnum):
    CURRENT_EXCHANGE = "current_exchange"
    NEXT_EXCHANGE = "next_exchange"


class ACTIONS(StrEnum):
    HANGUP = "hangup"
