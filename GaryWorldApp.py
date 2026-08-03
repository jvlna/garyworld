# Annalise Pasztor

import random
import os
import streamlit as st

st.set_page_config(page_title="Gary's Adventure", page_icon="\U0001F43E", layout="wide")

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

# ************************************* Style CSS *************************************

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1000px;
        margin-left: auto;
        margin-right: auto;
    }
    h1, h2, h3, p, .stMarkdown, .stCaption, .stAlert {
        text-align: center;
    }
    .stButton, [data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }
    .stButton > button, [data-testid="stButton"] button {
        width: 100%;
        max-width: 420px;
    }
    .stImage img, [data-testid="stImage"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .stNumberInput, .stRadio, [data-testid="stNumberInput"], [data-testid="stRadio"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ************************************* Locations *************************************
LOCATIONS = {
    "Park": {
        "name": "Park",
        "description": "A nice spot to sniff around.",
        "coordinates": (20.908705971114415, -100.74281147020744),
    },
    "CarrotFarm": {
        "name": "Don Toño's Carrot Farm",
        "description": "Ripe for harvest.",
        "coordinates": (20.87068248096162, -100.74540747491892),
    },
    "ElGanso": {
        "name": "Giant Goose",
        "description": "It's a giant building shaped like a goose. Can't miss it.",
        "coordinates": (20.89953709465775, -100.74745505605448),
    },
    "Parroquia": {
        "name": "La Parroquía",
        "description": "Big pink gothic-looking church. Maybe Princess Peach lives here.",
        "coordinates": (20.91378282095044, -100.74376994648449),
    },
}

BLIMP_SCENES = {
    "flight", "smoke_explode", "carrot_fishing", "carrot_eat_end",
    "carrot_throwing", "carrot_throwing_result", "wind_dilemma",
    "lasso_goose", "goose_tower", "combat_result", "good_evil",
}

# ************************************* Map *************************************
# Uses Streamlit's built-in st.map 

def render_map():
    import pandas as pd
    import pydeck as pdk
 
    loc = LOCATIONS[st.session_state.location]
    lat, lon = loc["coordinates"]
    df = pd.DataFrame({"lat": [lat], "lon": [lon], "name": [loc["name"]]})
 
    pin_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color=[220, 20, 60],
        get_radius=60,
    )
    label_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["lon", "lat"],
        get_text="name",
        get_size=16,
        get_color=[0, 0, 0],
        get_pixel_offset=[0, -18],  # nudges the label above the pin
        get_text_anchor='"middle"',
        get_alignment_baseline='"bottom"',
    )
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=13)
    deck = pdk.Deck(
        layers=[pin_layer, label_layer],
        initial_view_state=view_state,
        map_style="light_no_labels",
        tooltip=False,
    )
    st.pydeck_chart(deck, width=250, height=250)

# ************************************* Session state *************************************

def init_state():
    """Runs once per browser session (first load)"""
    if "scene" not in st.session_state:
        reset_game()


def reset_game():
    """Equivalent to GarysAdventure.start() / restart()."""
    st.session_state.scene = "intro"
    st.session_state.location = "Park"
    # Mirrors the original Player.locations set: a de-duped record of every
    # spot Gary has been, for seePlayerLocations(). start() in the original
    # always sets currentLocation to Park first, so Park is visited from
    # the get-go.
    st.session_state.visited_locations = {"Park"}
    st.session_state.player_inventory = []
    st.session_state.blimp_inventory = {
        "Rope": 1,
        "Empty Victoria can": 1,
        "Pack of Marlboros": 1,
    }
    st.session_state.ending = None
    st.session_state.item_taken = False
    st.session_state.combat_roll = None
    st.session_state.last_jettison = 0
    st.session_state.wafers_eaten = 0
    st.session_state.god_combat_roll = None


def go_to(scene_key, location_key=None):
    """Small helper: set next scene (and optionally location), then rerun."""
    st.session_state.scene = scene_key
    if location_key:
        st.session_state.location = location_key
        st.session_state.visited_locations.add(LOCATIONS[location_key]["name"])
    st.rerun()


def centered_button(*args, **kwargs):
    """Drop-in replacement for st.button, utting
    the button inside spacer columns to physically center it in the layout, which works regardless of Streamlit's internal DOM/CSS.
    """
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        kwargs.setdefault("use_container_width", True)
        return st.button(*args, **kwargs)


# ************************************* Images *************************************
# Add an optional illustration for a scene by dropping a file named
# images/<scene_key>.png (or .jpg) into the images/ folder. If it's not there, the
# scene just renders without one — nothing breaks.
#
# Each call can format the image differently:
#   show_scene_image("start")                                   -> full column width
#   show_scene_image("goose_tower", width=250)                  -> fixed size, centered
#   show_scene_image("game_won", width=300, caption="The end.") -> fixed size + caption
#   show_scene_image("flight", align="left")                    -> full width, but if
#                                                                    you also pass width,
#                                                                    "left"/"right" skips
#                                                                    the centering columns


def show_scene_image(scene_key, width=None, caption=None, align="center"):
    for ext in ("png", "jpg", "jpeg", "gif"):
        path = os.path.join(IMAGE_DIR, f"{scene_key}.{ext}")
        if os.path.exists(path):
            if width and align == "center":
                # Fixed pixel width, centered using the same spacer-column
                # trick as centered_button — st.image's own centering isn't
                # reliable for anything narrower than the full column.
                left, mid, right = st.columns([1, 2, 1])
                with mid:
                    st.image(path, width=width, caption=caption)
            elif width:
                # Fixed pixel width, left- or right-aligned (no spacer columns).
                st.image(path, width=width, caption=caption)
            else:
                st.image(path, use_container_width=True, caption=caption)
            return


# ************************************* Scenes *************************************

def scene_intro():
    st.write("### Welcome to Gary's World.")
    show_scene_image("scene_intro", width=350)
    st.write("You are a small, anxious dog.")
    st.write("Even small, anxious dogs have to be brave sometimes.")
    if centered_button("BEGIN ADVENTURE", type="primary"):
        go_to("start")


def scene_start():
    show_scene_image("start")
    st.write(
        "Your daily neighborhood stroll has taken a turn for the worse when a large "
        "street dog makes eye contact. He starts charging towards you."
    )
    if centered_button("Fight"):
        go_to("fight_end")
    if centered_button("Flight"):
        go_to("flight")


def scene_fight_end():
    show_scene_image("fight_end")
    st.write("You turn and face your aggressor.")
    st.error("You have been eaten by a belgian malinois. Game over.")
    show_restart_button()


def scene_flight():
    show_scene_image("flight")
    st.write(
        "The ground is no longer a safe option. Taking a look around, you spot "
        "something overhead. The empanada vendor on the corner has left their airship "
        "unattended. In a single jump, you grab the rope and use your elite "
        "tug-o-war skills to board the airship and break free."
    )
    show_scene_image("scene_intro", width=350)
    st.write(
        "The thrashing open mouth of the belgian malinois is becoming smaller and "
        "smaller. Whew!"
    )
    st.write(
        "Oh, wait. You are accelerating upwards alarmingly fast. Even though the vet "
        "said you are overweight, you still are not heavy enough to balance this "
        "airship. Maybe there's something lying around that could help?"
    )
    with st.expander("Check the blimpventory"):
        for item, qty in st.session_state.blimp_inventory.items():
            st.write(f"- {item} (quantity: {qty})")
        st.caption(
            "Well, guess we don't have much to work with. But hey, they don't call "
            "you 'Cowboy Gary' for nothin'."
        )
    st.write(
        "You scan the horizon. To the south is farmland, namely, Don Toño's Carrot "
        "Farm. To the east, a large flock of geese is flying in formation."
    )
    st.write(
        "Access your inventory and map at any time during the game by expanding the menu in the top left corner."
    )
    with st.expander("\U0001F5FA\uFE0F Map", expanded=True):
            render_map()
    st.write("You consider your options:")
    if centered_button("Go south to lasso carrots for ballast."):
        go_to("carrot_fishing", "CarrotFarm")
    if centered_button("Head east to lasso a goose."):
        go_to("lasso_goose", "ElGanso")
    if centered_button("Take a cigarette break."):
        roulette = random.randint(0, 2)
        if roulette == 1:
            go_to("smoke_explode")
        else:
            st.info(
                "Smoking is very bad for you, especially on a hydrogen-filled "
                "airship. You haven't exploded this time, but who knows about the "
                "next. Take it easy on the smoke breaks, eh?"
            )


def scene_smoke_explode():
    show_scene_image("smoke_explode")
    st.error(
        "Smoking is very bad for you, especially on a hydrogen-filled airship. "
        "Everything has exploded. Game over."
    )
    show_restart_button()


def scene_carrot_fishing():
    show_scene_image("carrot_fishing")
    st.write(
        "You fashion the rope into a lasso and toss it towards the carrot stalks. "
        "Huzzah! They are being ripped out of the ground at an impressive rate."
    )
    st.session_state.blimp_inventory["Carrots"] = 500
    st.write(
        f"New blimp inventory acquired: "
        f"{st.session_state.blimp_inventory['Carrots']} carrots."
    )
    st.write(
        "Your lasso technique was too good. The airship basket is overflowing with "
        "carrots and the airship starts to sink."
    )
    if centered_button("Jettison carrots overboard."):
        go_to("carrot_throwing")
    if centered_button("Eat the carrots."):
        go_to("carrot_eat_end")


def scene_carrot_eat_end():
    show_scene_image("carrot_eat_end")
    st.error(
        "This did not work. The carrots are stuck in your belly and you are "
        "rapidly sinking to your demise. Game over."
    )
    show_restart_button()


def scene_carrot_throwing():
    show_scene_image("carrot_throwing")
    current = st.session_state.blimp_inventory["Carrots"]
    st.write(f"You currently have {current} carrots aboard.")
    jettison = st.number_input(
        "How many carrots would you like to toss overboard?",
        min_value=0,
        max_value=current,
        step=20,
        key="jettison_amount",
    )
    if centered_button("Toss them overboard", type="primary"):
        new_amount = current - jettison
        st.session_state.blimp_inventory["Carrots"] = new_amount
        st.session_state.last_jettison = jettison
        st.session_state.scene = "carrot_throwing_result"
        st.rerun()


def scene_carrot_throwing_result():
    show_scene_image("carrot_throwing_result")
    jettison = st.session_state.get("last_jettison", 0)
    remaining = st.session_state.blimp_inventory["Carrots"]
    st.write(
        f"You toss {jettison} carrots overboard. You hear a distant scream from "
        "below, but that is none of your business."
    )
    st.write(f"You now have {remaining} carrots.")
    if remaining > 300:
        st.warning("You are still sinking. Let's throw some more.")
        if centered_button("Keep throwing"):
            go_to("carrot_throwing")
    elif remaining < 150:
        st.error(
            "You have thrown too many carrots. You ascend rapidly and freeze to "
            "death in the stratosphere. Game over."
        )
        show_restart_button()
    else:
        st.success(
            "Nice! You have found the sweet spot of carrot ballast. The airship "
            "levels out."
        )
        if centered_button("Continue", type="primary"):
            go_to("wind_dilemma")


def scene_wind_dilemma():
    show_scene_image("wind_dilemma")
    st.write(
        "Ah geez. If it's not one thing, it's another. The wind is picking up and "
        "this airship is getting hard to control."
    )
    if centered_button("Maybe now we should lasso that goose for steering help."):
        go_to("lasso_goose", "ElGanso")
    if centered_button("I trust the winds to take me where I am meant to be."):
        go_to("parroquia", "Parroquia")


def scene_parroquia():
    show_scene_image("parroquia")
    st.write(
        "Fiddlesticks. The winds have impaled your airship on the pink spires of "
        "La Parroquía de San Miguel Arcángel."
    )
    if centered_button("Sneak inside and disguise yourself as a priest."):
        go_to("priest_gary")
    if centered_button(
        "\u201cWell, now that we're here at church, guess it's time to fight "
        "God,\u201d your chihuahua ancestors whisper to you."
    ):
        go_to("fight_god")


def scene_priest_gary():
    show_scene_image("priest_gary")
    st.write(
        "You abandon your airship and climb into a window. After a short search, "
        "you find a priest and yank his robe off. You are now Priest Gary."
    )
    st.write("You slip into the secret chambers and find a treat: communion wafers!")
    wafers = st.number_input(
        "How many would you like to eat?",
        min_value=0,
        step=1,
        key="wafers_input",
    )
    if centered_button("Eat them", type="primary"):
        st.session_state.wafers_eaten = wafers
        st.session_state.scene = "priest_gary_result"
        st.rerun()


def scene_priest_gary_result():
    show_scene_image("priest_gary_result")
    wafers = st.session_state.get("wafers_eaten", 0)
    if wafers > 20:
        st.error(
            "That was a lot of wafers, buddy. You fall asleep and are discovered "
            "by the real priest. You are exiled for your crimes. Game over."
        )
        show_restart_button()
    else:
        st.write(
            "You are feeling re-energized and infused with the holy spirit. It "
            "is now time to fight God."
        )
        if centered_button("Continue", type="primary"):
            go_to("fight_god")


def scene_fight_god():
    show_scene_image("fight_god")
    st.write(
        "You climb to the top of the church's tallest spire and yip your "
        "loudest yap. A clap of thunder booms throughout the city in response. "
        "The time has come to fight God."
    )
    if centered_button("\U0001F3B2 Roll the 20-sided die", type="primary"):
        combat = random.randint(1, 20)
        st.session_state.god_combat_roll = combat
        st.session_state.scene = "fight_god_result"
        st.rerun()


def scene_fight_god_result():
    show_scene_image("fight_god_result")
    combat = st.session_state.get("god_combat_roll", 0)
    if combat > 15:
        st.write(
            f"You rolled a {combat}. You leap into the air, and, trusting the "
            "guidance of your ancestors, sink your little canines into the "
            "heavenly ankle, God's one weakness. The sky turns purple. You have "
            "killed God. You, Gary, are the new Ruler of the Universe."
        )
        if centered_button("Continue", type="primary"):
            go_to("good_evil")
    else:
        st.error(
            f"You rolled a {combat}. God sends down a lightning bolt and fries "
            "you to a tiny little crisp. Game over."
        )
        show_restart_button()


def scene_lasso_goose():
    show_scene_image("lasso_goose")
    st.write(
        "Whoa there, cowboy! You have caught the lead goose! No easy feat. You now seem to be taking a steep dive downwards."
    )
    st.write(
        "As you get closer to earth, you see where the geese are headed. It's a "
        "massive structure looming over the city, curiously shaped like a goose. "
        "It seems the flock is returning home to the mothership."
    )
    if centered_button("Dock your airship at the beak of the giant goose structure."):
        go_to("goose_tower", "ElGanso")
    if centered_button("You've heard there's a madman living in the goose building. Release the goose and try your luck with the carrots."):
        st.write("You un-lasso the lead goose and head south.")
        go_to("carrot_fishing", "CarrotFarm")


def scene_goose_tower():
    show_scene_image("goose_tower")
    st.write("Airship docking successful.")
    st.write("Before disembarking, would you like to take any of the blimp inventory with you?")

    remaining_items = list(st.session_state.blimp_inventory.keys())
    if remaining_items and not st.session_state.get("item_taken"):
        choice = st.radio("You can take one item with you:", remaining_items)
        if centered_button("Take item"):
            st.session_state.player_inventory.append(choice)
            st.session_state.blimp_inventory.pop(choice)
            st.session_state.item_taken = True
            st.rerun()
    else:
        st.write(
            "Right then. You disembark the blimp through the beak of the giant "
            "goose. Upon entering through the esophagoose, a voice booms from the "
            "darkness:"
        )
        st.write("**>> Who dares enter my tower?**")
        st.write("With a flourish of robes, a wizard appears.")
        st.write("**>> My, what lovely patitas you have. Just what I need...**")
        st.write(
            "Oh geez. Seems like the wizard is going to try and steal your patitas, "
            "maybe to eat them in a stew? Or perhaps for a spell."
        )
        st.write(
            "You look back. The goose has closed its beak. There's no way back "
            "out. Combat is your only option."
        )
        if centered_button("\U0001F3B2 Roll the 20-sided die", type="primary"):
            combat = random.randint(1, 20)
            st.session_state.combat_roll = combat
            st.session_state.scene = "combat_result"
            st.rerun()


def scene_combat_result():
    show_scene_image("combat_result")
    combat = st.session_state.get("combat_roll", 0)
    has_can = any("can" in item.lower() for item in st.session_state.player_inventory)
    has_marlboros = any(
        "marlboro" in item.lower() for item in st.session_state.player_inventory
    )
    if combat > 10:
        st.write(
            f"You rolled a {combat}. You are given firebreathing abilities and in "
            "one big huff and puff you incinerate the wizard. The goose tower is "
            "now yours. 'Gary the Goose Lord' has a nice ring to it."
        )
        if centered_button("Continue", type="primary"):
            go_to("good_evil")
    elif combat == 10 and has_can:
        st.write(
            "You have rolled a 10. You and the wizard are an equal match... but "
            "just as you begin to tire, you realize you have a rusty old Victoria "
            "can with you."
        )
        st.write(
            "You quickly fashion it into a ninja star and throw it at the wizard. "
            "Victory is yours, and so is the tower! 'Gary the Goose Lord' has a "
            "nice ring to it."
        )
        if centered_button("Continue", type="primary"):
            go_to("good_evil")
    elif combat == 10 and has_marlboros:
        st.write(
            "You have rolled a 10. You and the wizard are an equal match... but "
            "you realize you have your pack of Marlboros with you."
        )
        st.write(
            "You offer the wizard a smoke. She accepts, and confides in you that "
            "she's quite tired of her current life. She's always dreamed of a "
            "tower by the sea... She decides to go for it, and asks that you take "
            "over her tower and duties here. 'Gary the Goose Lord' has a nice "
            "ring to it."
        )
        if centered_button("Continue", type="primary"):
            go_to("good_evil")
    else:
        st.error(
            f"You rolled a {combat}. The wizard has defeated you and stolen your "
            "adorable little patitas. Game over."
        )
        show_restart_button()


def scene_good_evil():
    show_scene_image("good_evil")
    st.write(
        "You are now all-powerful. One final question remains. Will you remain "
        "pure of heart, or allow your power to corrupt you?"
    )
    if centered_button("Return the blimp to its rightful owner, the empanada vendor."):
        st.session_state.player_inventory.append("***The Golden Empanada***")
        st.session_state.ending = "good"
        go_to("game_won")
    if centered_button("Keep everything for yourself. You've earned it."):
        st.session_state.ending = "evil"
        go_to("game_won")


def scene_game_won():
    show_scene_image("game_won")
    st.success("Congratulations, you won!")
    if st.session_state.ending == "good":
        st.write(
            "Who's a good boy? You are! Upon returning the airship, the empanada "
            "vendor expresses their gratitude by gifting you their tastiest empanada."
        )
    else:
        st.write(
            "You have won the game, but lost your status as a good boy. Oh well! "
            "Time to chase some geese."
        )
    st.write("All in all, a pretty good day to be an anxious little dog.")
    st.write("*Courage is not the absence of fear, but the triumph over it.*")
    show_restart_button()


def show_journey_summary():
    with st.expander("Show Journey Summary"):
        st.write("**\U0001F4CD Spots visited:**")
        for loc in sorted(st.session_state.visited_locations):
            st.write(f"- {loc}")
        if st.session_state.player_inventory:
            st.write("**\U0001F392 Inventory:**")
            for item in st.session_state.player_inventory:
                st.write(f"- {item}")


def show_restart_button():
    show_journey_summary()
    st.write("")
    if centered_button("\U0001F501 Start over"):
        reset_game()
        st.rerun()


SCENES = {
    "intro": scene_intro,
    "start": scene_start,
    "fight_end": scene_fight_end,
    "flight": scene_flight,
    "smoke_explode": scene_smoke_explode,
    "carrot_fishing": scene_carrot_fishing,
    "carrot_eat_end": scene_carrot_eat_end,
    "carrot_throwing": scene_carrot_throwing,
    "carrot_throwing_result": scene_carrot_throwing_result,
    "wind_dilemma": scene_wind_dilemma,
    "parroquia": scene_parroquia,
    "priest_gary": scene_priest_gary,
    "priest_gary_result": scene_priest_gary_result,
    "fight_god": scene_fight_god,
    "fight_god_result": scene_fight_god_result,
    "lasso_goose": scene_lasso_goose,
    "goose_tower": scene_goose_tower,
    "combat_result": scene_combat_result,
    "good_evil": scene_good_evil,
    "game_won": scene_game_won,
}

# ************************************* Menu bar *************************************
# Quick-access popups for personal inventory, blimp inventory, and the map.
# Hidden on the intro screen since there's nothing to show yet.

def show_sidebar():
    if st.session_state.scene == "intro":
        return
        
    with st.sidebar:
        st.header("\U0001F43E Gary Menu")
        with st.expander("\U0001F43E Personal Inventory"):
            if st.session_state.player_inventory:
                for item in st.session_state.player_inventory:
                    st.write(f"- {item}")
            else:
                st.caption("Empty so far.")
        with st.expander("\U0001F388 Blimp Inventory"):
            if st.session_state.blimp_inventory in BLIMP_SCENES:
                for item, qty in st.session_state.blimp_inventory.items():
                    st.write(f"- {item} (quantity: {qty})")
            else:
                st.caption("Nothing left aboard.")
        with st.expander("\U0001F5FA\uFE0F Map", expanded=True):
            render_map()

# ************************************* Main *************************************

init_state()

show_sidebar()
SCENES[st.session_state.scene]()

