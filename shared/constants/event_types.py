from enum import Enum


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    FORM_SUBMIT = "form_submit"
    SIGNUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    PURCHASE = "purchase"
    CUSTOM = "custom"


EVENT_TYPE_ALIASES = {
    "pv": EventType.PAGE_VIEW,
    "click": EventType.CLICK,
    "scroll": EventType.SCROLL,
    "form": EventType.FORM_SUBMIT,
    "signup": EventType.SIGNUP,
    "login": EventType.LOGIN,
    "logout": EventType.LOGOUT,
    "purchase": EventType.PURCHASE,
    "custom": EventType.CUSTOM,
}


INTERVAL_MAP = {
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "week": 604800,
}