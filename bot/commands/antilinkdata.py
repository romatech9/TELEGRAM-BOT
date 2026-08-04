from collections import defaultdict

# ==========================================
# MUFASER-X Anti-Link Database
# ==========================================

# Each group has its own settings
antilink_settings = defaultdict(
    lambda: {
        "enabled": False,
        "mode": None,          # warn, ban, kick, delete
        "warn_limit": 3,
        "mute_time": 20,       # minutes
    }
)


# Store user warnings
# antilink_warnings[group_id][user_id] = count

antilink_warnings = defaultdict(
    lambda: defaultdict(int)
)


# ==========================================
# MODE FUNCTIONS
# ==========================================

def set_mode(chat_id, mode):
    """
    Enable one Anti-Link mode.
    Automatically replaces old mode.
    """

    antilink_settings[chat_id]["enabled"] = True
    antilink_settings[chat_id]["mode"] = mode


def disable_antilink(chat_id):
    """
    Turn Anti-Link OFF.
    """

    antilink_settings[chat_id]["enabled"] = False
    antilink_settings[chat_id]["mode"] = None


def get_mode(chat_id):
    """
    Get current mode.
    """

    return antilink_settings[chat_id]["mode"]


def is_enabled(chat_id):
    """
    Check if Anti-Link is ON.
    """

    return antilink_settings[chat_id]["enabled"]


# ==========================================
# WARNING SYSTEM
# ==========================================

def add_warning(chat_id, user_id):

    antilink_warnings[chat_id][user_id] += 1

    return antilink_warnings[chat_id][user_id]


def get_warning(chat_id, user_id):

    return antilink_warnings[chat_id].get(user_id, 0)


def reset_warning(chat_id, user_id):

    antilink_warnings[chat_id][user_id] = 0


def warning_limit(chat_id):

    return antilink_settings[chat_id]["warn_limit"]


def mute_time(chat_id):

    return antilink_settings[chat_id]["mute_time"]


def warning_reached(chat_id, user_id):

    return get_warning(chat_id, user_id) >= warning_limit(chat_id)