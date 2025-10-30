from rest_framework.throttling import UserRateThrottle


class InviteThrottle(UserRateThrottle):
    scope = "invite"
