import streamlit as st

st.title("🧩 Cryptid Tracker (Advanced Visibility Controls)")

# -------------------------
# CONFIG
# -------------------------
DEFAULT_PLAYERS = 4

# -------------------------
# GLOBAL TOGGLES (TOP OF APP)
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
        "🚫 Hide ALL false (eliminated) clues",
        value=st.session_state.hide_all_false
    )

# -------------------------
# PLAYER NAMES
# -------------------------
if "player_names" not in st.session_state:
    st.session_state.player_names = [f"Player {i+1}" for i in range(DEFAULT_PLAYERS)]

st.subheader("✏️ Rename Players")

for i in range(DEFAULT_PLAYERS):
    st.session_state.player_names[i] = st.text_input(
        f"Player {i+1}",
        value=st.session_state.player_names[i],
        key=f"name_{i}"
    )

players = st.session_state.player_names

# -------------------------
# RULES
# -------------------------
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
    "Within 2 bear",
    "Within 2 cougar",
    "Within 2 stone",
    "Within 2 shack",
    "Within 3 colored structures"
]

terrains = ["Forest", "Desert", "Water", "Swamp", "Mountain"]

# -------------------------
# STATE
# -------------------------
if "state" not in st.session_state:
    st.session_state.state = {
        f"Player {i+1}": {r: "inactive" for r in rules}
        for i in range(DEFAULT_PLAYERS)
    }

for p in players:
    if p not in st.session_state.state:
        st.session_state.state[p] = {r: "inactive" for r in rules}

# -------------------------
# STATE CYCLE
# -------------------------
def cycle_state(current):
    if current == "inactive":
        return "active"
    if current == "active":
        return "eliminated"
    return "inactive"

# -------------------------
# SOLVER
# -------------------------
def solve_player(player):
    state = st.session_state.state[player]

    possible = set(terrains)

    for rule, status in state.items():

        if status == "eliminated":
            if " or " in rule:
                a, b = rule.split(" or ")
                possible.discard(a.strip())
                possible.discard(b.strip())
            continue

        elif status == "active":
            if " or " in rule:
                a, b = rule.split(" or ")
                possible &= {a.strip(), b.strip()}
            continue

    return sorted(possible)

# -------------------------
# UI
# -------------------------
for player in players:
    st.subheader(player)

    # PER PLAYER TOGGLES
    col1, col2 = st.columns(2)

    with col1:
        hide_inactive = st.toggle(
            f"🙈 Hide inactive clues ({player})",
            key=f"hide_inactive_{player}"
        )

    with col2:
        hide_false = st.toggle(
            f"🚫 Hide false clues ({player})",
            key=f"hide_false_{player}"
        )

    cols = st.columns([2, 1])

    with cols[0]:
        for rule in rules:

            state = st.session_state.state[player][rule]

            # -------------------------
            # GLOBAL + LOCAL FILTER LOGIC
            # -------------------------
            if (st.session_state.hide_all_inactive or hide_inactive) and state == "inactive":
                continue

            if (st.session_state.hide_all_false or hide_false) and state == "eliminated":
                continue

            icon = (
                "⚪" if state == "inactive"
                else "🟢" if state == "active"
                else "🔴"
            )

            label = f"{icon} {rule}"

            if st.button(label, key=f"{player}_{rule}"):
                st.session_state.state[player][rule] = cycle_state(state)
                st.rerun()

    with cols[1]:
        st.write("🌍 Possible Terrains")
        st.write(" | ".join(solve_player(player)))