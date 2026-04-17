import streamlit as st

st.title("🧩 Cryptid Tracker")

# -------------------------
# CONFIG
# -------------------------
terrains = ["Forest", "Desert", "Water", "Swamp", "Mountain"]

terrain_rules = [f"{a} or {b}" for i, a in enumerate(terrains) for b in terrains[i+1:]]

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
num_players = st.number_input("👥 Number of players", 2, 5, 4)

# -------------------------
# GLOBAL TOGGLES
# -------------------------
if "hide_all_inactive" not in st.session_state:
    st.session_state.hide_all_inactive = False

if "hide_all_eliminated" not in st.session_state:
    st.session_state.hide_all_eliminated = False

colg1, colg2 = st.columns(2)

with colg1:
    st.session_state.hide_all_inactive = st.toggle(
        "🙈 Hide ALL inactive rules",
        value=st.session_state.hide_all_inactive
    )

with colg2:
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

players = st.session_state.player_names

st.warning("Legend:\n\n⚪ Unknown / Inactive\n🔴 False / Eliminated\n🟢 True")

# -------------------------
# STATE INIT
# -------------------------
if "terrain_state" not in st.session_state:
    st.session_state.terrain_state = {
        p: {t: "inactive" for t in terrains} for p in players
    }

if "rule_state" not in st.session_state:
    st.session_state.rule_state = {
        p: {r: "inactive" for r in rules} for p in players
    }

# -------------------------
# STATE CYCLE
# -------------------------
def cycle(s):
    return "eliminated" if s == "inactive" else "active" if s == "eliminated" else "inactive"

# -------------------------
# MATRIX LOGIC
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

    # terrain filters
    for t, s in st.session_state.terrain_state[player].items():
        if s == "active":
            possible = {t}
        elif s == "eliminated":
            possible.discard(t)

    # rule filters
    for rule, s in st.session_state.rule_state[player].items():
        if " or " not in rule:
            continue

        a, b = rule.split(" or ")
        a, b = a.strip(), b.strip()

        if s == "active":
            possible &= {a, b}
        elif s == "eliminated":
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
        hide_inactive = st.toggle("🙈 Hide inactive", key=f"hi_{player}")

    with col2:
        hide_eliminated = st.toggle("🚫 Hide eliminated", key=f"he_{player}")

    cols = st.columns([2, 3])

    # -------------------------
    # INPUTS
    # -------------------------
    with cols[0]:
        st.write("🎯 Terrain")

        for t in terrains:
            s = st.session_state.terrain_state[player][t]
            icon = "⚪" if s == "inactive" else "🔴" if s == "eliminated" else "🟢"

            if st.button(f"{icon} {t}", key=f"{player}_t_{t}"):
                st.session_state.terrain_state[player][t] = cycle(s)
                st.rerun()

        st.write("---")
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
    # MATRIX + OUTPUT
    # -------------------------
    with cols[1]:
        st.write("🌍 Terrain Matrix")

        header = st.columns(len(terrains) + 1)
        header[0].write("")
        for i, t in enumerate(terrains):
            header[i + 1].markdown(f"**{t[:3]}**")

        for t1 in terrains:
            row = st.columns(len(terrains) + 1)
            row[0].markdown(f"**{t1[:3]}**")

            for j, t2 in enumerate(terrains):
                row[j + 1].markdown(get_cell(player, t1, t2))

        possible = solve(player)
