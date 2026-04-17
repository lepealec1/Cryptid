import streamlit as st

st.title("🧩 Cryptid Tracker")

# -------------------------
# CONFIG
# -------------------------
terrains = ["Forest", "Desert", "Water", "Swamp", "Mountain"]

terrain_rules = [
    f"{a} or {b}"
    for i, a in enumerate(terrains)
    for b in terrains[i + 1:]
]

other_rules = [
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

rules = terrain_rules + other_rules

# -------------------------
# PLAYER COUNT
# -------------------------
num_players = int(st.number_input("👥 Number of players", 2, 5, 4))

# -------------------------
# GLOBAL TOGGLES
# -------------------------
st.session_state.setdefault("hide_all_inactive", False)
st.session_state.setdefault("hide_all_eliminated", False)

c1, c2 = st.columns(2)
with c1:
    st.session_state.hide_all_inactive = st.toggle(
        "🙈 Hide ALL inactive rules",
        value=st.session_state.hide_all_inactive
    )

with c2:
    st.session_state.hide_all_eliminated = st.toggle(
        "🚫 Hide ALL eliminated rules",
        value=st.session_state.hide_all_eliminated
    )

# -------------------------
# PLAYERS
# -------------------------
def resize_list(lst, size, default_func):
    lst = list(lst)
    if len(lst) < size:
        lst += [default_func(i) for i in range(len(lst), size)]
    return lst[:size]

st.session_state.setdefault("player_names", [])

st.session_state.player_names = resize_list(
    st.session_state.player_names,
    num_players,
    lambda i: f"Player {i+1}"
)

st.subheader("✏️ Rename Players")

for i in range(num_players):
    st.session_state.player_names[i] = st.text_input(
        f"Player {i+1}",
        value=st.session_state.player_names[i],
        key=f"name_{i}"
    )

players = st.session_state.player_names[:num_players]

st.warning("⚪ Unknown / Inactive | 🔴 Eliminated | 🟢 Active")

# -------------------------
# STATE INIT
# -------------------------
def init_state():
    if "terrain_state" not in st.session_state:
        st.session_state.terrain_state = {}

    if "rule_state" not in st.session_state:
        st.session_state.rule_state = {}

    for p in players:
        if p not in st.session_state.terrain_state:
            st.session_state.terrain_state[p] = {t: "inactive" for t in terrains}

        if p not in st.session_state.rule_state:
            st.session_state.rule_state[p] = {r: "inactive" for r in rules}

init_state()

# -------------------------
# CYCLE STATE
# -------------------------
def cycle(s):
    if s == "inactive":
        return "eliminated"
    if s == "eliminated":
        return "active"
    return "inactive"

# -------------------------
# MATRIX CELL
# -------------------------
def get_cell(player, t1, t2):
    s1 = st.session_state.terrain_state[player][t1]
    s2 = st.session_state.terrain_state[player][t2]

    if s1 == "eliminated" or s2 == "eliminated":
        return "🔴"
    if s1 == "active" or s2 == "active":
        return "🟢"
    return "⚪"

# -------------------------
# SOLVER
# -------------------------
def solve(player):
    possible = set(terrains)

    for t, s in st.session_state.terrain_state[player].items():
        if s == "active":
            possible = {t}
        elif s == "eliminated":
            possible.discard(t)

    for rule, s in st.session_state.rule_state[player].items():
        if " or " not in rule:
            continue

        a, b = [x.strip() for x in rule.split(" or ")]

        if s == "active":
            possible &= {a, b}
        elif s == "eliminated":
            possible.discard(a)
            possible.discard(b)

    return sorted(possible)

# -------------------------
# PLAYER UI (SINGLE COLUMN)
# -------------------------
for player in players:
    st.subheader(player)

    hide_inactive = st.toggle("🙈 Hide inactive", key=f"hi_{player}")
    hide_eliminated = st.toggle("🚫 Hide eliminated", key=f"he_{player}")

    # -------------------------
    # TERRAIN BUTTONS
    # -------------------------
    st.write("🎯 Terrain")

    for t in terrains:
        s = st.session_state.terrain_state[player][t]
        icon = "⚪" if s == "inactive" else "🔴" if s == "eliminated" else "🟢"

        if st.button(f"{icon} {t}", key=f"{player}_t_{t}"):
            st.session_state.terrain_state[player][t] = cycle(s)
            st.rerun()

    # -------------------------
    # MATRIX (FIRST)
    # -------------------------
    st.write("🌍 Terrain Matrix")

    header = "|     | " + " | ".join(t[:3] for t in terrains) + " |"
    divider = "|" + "----|" * (len(terrains) + 1)

    rows = []
    for t1 in terrains:
        row = [t1[:3]]
        for t2 in terrains:
            row.append(get_cell(player, t1, t2))
        rows.append("| " + " | ".join(row) + " |")

    table = "\n".join([header, divider] + rows)
    st.markdown(table)

    # -------------------------
    # OTHER RULES (AFTER MATRIX)
    # -------------------------
    st.write("📋 Other Clues")

    for rule in other_rules:
        s = st.session_state.rule_state[player][rule]

        if (st.session_state.hide_all_inactive or hide_inactive) and s == "inactive":
            continue
        if (st.session_state.hide_all_eliminated or hide_eliminated) and s == "eliminated":
            continue

        icon = "⚪" if s == "inactive" else "🔴" if s == "eliminated" else "🟢"

        if st.button(f"{icon} {rule}", key=f"{player}_r_{rule}"):
            st.session_state.rule_state[player][rule] = cycle(s)
            st.rerun()

    # -------------------------
    # POSSIBLE RESULTS
    # -------------------------
    