import streamlit as st

st.title("🧩 Cryptid Tracker")

# -------------------------
# CONFIG
# -------------------------
terrains = ["Forest", "Desert", "Water", "Swamp", "Mountain"]

rules = [
    "Forest or Desert",
    "Forest or Water",
    "Forest or Swamp",
    "Forest or Mountain",
    "Desert or Water",
    "Desert or Swamp",
    "Desert or Mountain",
    "Water or Swamp",
    "Water or Mountain",
    "Swamp or Mountain",
    "Within 1 Forest",
    "Within 1 Desert",
    "Within 1 Water",
    "Within 1 Swamp",
    "Within 1 Mountain",
    "Within 1 animal",
    "Within 2 bear (black)",
    "Within 2 cougar (red)",
    "Within 2 of a standing stone ⬡",
    "Within 2 of an abandoned shack △",
    "Within 3 of a blue structure ⬡ or △",
    "Within 3 of a white structure ⬡ or △",
    "Within 3 of a green structure ⬡ or △"
]

# -------------------------
# PLAYER COUNT
# -------------------------
num_players = st.number_input(
    "👥 Number of players",
    min_value=2,
    max_value=5,
    value=4,
    step=1
)

# -------------------------
# GLOBAL TOGGLES
# -------------------------
if "hide_all_inactive" not in st.session_state:
    st.session_state.hide_all_inactive = False

if "hide_all_false" not in st.session_state:
    st.session_state.hide_all_false = False

colg1, colg2 = st.columns(2)

with colg1:
    st.session_state.hide_all_inactive = st.toggle(
        "🙈 Hide ALL inactive clues",
        value=st.session_state.hide_all_inactive
    )

with colg2:
    st.session_state.hide_all_false = st.toggle(
        "🚫 Hide ALL false clues",
        value=st.session_state.hide_all_false
    )

# -------------------------
# PLAYERS (DYNAMIC)
# -------------------------
def resize_list(lst, size, default_func):
    lst = list(lst)
    if len(lst) < size:
        lst += [default_func(i) for i in range(len(lst), size)]
    return lst[:size]

if "player_names" not in st.session_state:
    st.session_state.player_names = []

st.session_state.player_names = resize_list(
    st.session_state.player_names,
    int(num_players),
    lambda i: f"Player {i+1}"
)

st.subheader("✏️ Rename Players")

for i in range(int(num_players)):
    st.session_state.player_names[i] = st.text_input(
        f"Player {i+1}",
        value=st.session_state.player_names[i],
        key=f"name_{i}"
    )

st.warning("Legend:\n\n⚪ Inactive Clue\n🟢 True Clue\n🔴 False Clue")

players = st.session_state.player_names

# -------------------------
# STATE INIT
# -------------------------
if "state" not in st.session_state:
    st.session_state.state = {
        p: {r: "inactive" for r in rules} for p in players
    }

# Add missing players
for p in players:
    if p not in st.session_state.state:
        st.session_state.state[p] = {r: "inactive" for r in rules}

# Remove deleted players
for p in list(st.session_state.state.keys()):
    if p not in players:
        del st.session_state.state[p]

# -------------------------
# STATE CYCLE
# -------------------------
def cycle_state(s):
    if s == "inactive":
        return "active"
    if s == "active":
        return "eliminated"
    return "inactive"

# -------------------------
# SOLVER
# -------------------------
def solve_player(player):
    state = st.session_state.state[player]

    possible = set(terrains)

    for rule, status in state.items():

        if " or " not in rule:
            continue

        a, b = rule.split(" or ")
        a, b = a.strip(), b.strip()

        if status == "active":
            possible &= {a, b}

        elif status == "eliminated":
            possible.discard(a)
            possible.discard(b)

    return sorted(possible)

# -------------------------
# UI
# -------------------------
for player in players:
    st.subheader(player)

    col1, col2 = st.columns(2)

    with col1:
        hide_inactive = st.toggle("🙈 Hide inactive", key=f"hide_inactive_{player}")

    with col2:
        hide_false = st.toggle("🚫 Hide false", key=f"hide_false_{player}")

    cols = st.columns([3, 1])

    # -------------------------
    # RULES
    # -------------------------
    with cols[0]:
        for rule in rules:
            status = st.session_state.state[player][rule]

            if (st.session_state.hide_all_inactive or hide_inactive) and status == "inactive":
                continue
            if (st.session_state.hide_all_false or hide_false) and status == "eliminated":
                continue

            icon = "⚪" if status == "inactive" else "🟢" if status == "active" else "🔴"

            if st.button(f"{icon} {rule}", key=f"{player}_{rule}"):
                st.session_state.state[player][rule] = cycle_state(status)
                st.rerun()

    # -------------------------
    # SOLVER OUTPUT
    # -------------------------
    with cols[1]:
        st.write("🌍 Possible Terrains")
        st.write(" | ".join(solve_player(player)))