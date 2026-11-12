from drafter import *
from dataclasses import dataclass
from bakery import assert_equal

@dataclass
class Observation:
    """Stores a single astronomy observation."""
    object_name: str
    object_type: str
    visibility: int
    cloudy: bool
    notes: str
    date: str

@dataclass
class State:
    """Stores all data for the Astronomy Observation Logbook."""
    observations: list[Observation]
    favorite_objects: dict[str, Observation]
    total_observations: int
    sky_message: str
    last_object_viewed: str


@route
def index(state: State) -> Page:
    """Home page."""
    return Page(state, [
        Header("Observation Logbook"),
        "Last viewed:",
        state.last_object_viewed,
        "Observations Logged:",
        str(state.total_observations),
        
        Button("Add Observation", add_observation_page),
        Button("Summary", summary_page),
        Button("Favorites", favorites_page),
        Button("Clear Log", clear_observations),
        Button("View Log", view_log_page),
    ])


@route
def add_observation_page(state: State) -> Page:
    """Page for entering observation data."""

    return Page(state, [
        Header("Add Observation"),

        "Object Name:",
        TextBox("object_name", ""),

        "Object Type:",
        SelectBox("object_type", ["Moon", "Planet", "Star", "Nebula", "Galaxy"]),

        "Date (e.g., YYYY-MM-DD):",
        TextBox("date", ""),
        
        "Visibility Rating: Bortle scale(1-9)",
        TextBox("visibility", ""),

        "Cloudy?",
        CheckBox("cloudy", False),

        "Add to Favorites?",
        CheckBox("favorite", False),

        "Notes:",
        TextArea("notes", ""),

        Button("Submit Observation", submit_observation),
        Button("Back Home", index)
    ])

@route
def submit_observation(state: State, object_name: str, object_type: str, date: str, visibility: str, cloudy: bool, favorite: bool, notes: str) -> Page:
    """Creates and stores an observation."""
    if visibility == "" or visibility is None:
        visibility = "5"
    try:
        vis_value = int(round(float(visibility)))
    except ValueError:
        vis_value = 5
        
    observation = Observation(
        object_name,
        object_type,
        vis_value,
        cloudy,
        notes,
        date
    )

    state.observations.append(observation)
    if favorite:
        state.favorite_objects[object_name] = observation
    
    state.total_observations += 1
    state.last_object_viewed = object_name

    if cloudy:
        state.sky_message = ("Cloudy skies affected visibility.")
    elif vis_value >= 7:
        state.sky_message = ("Heavy light pollution recorded.")
    elif object_type == "Planet":
        state.sky_message = ("Planet observation recorded!")
    else:
        state.sky_message = ("Observation saved successfully.")
    return Page(state, [
        Header("Observation Status"),
        state.sky_message,
        Button("Back Home", index)
    ])

@route
def summary_page(state: State) -> Page:
    """Displays summary statistics."""
    total_visibility = 0
    cloudy_count = 0
    for observation in state.observations:
        total_visibility += observation.visibility
        if observation.cloudy:
            cloudy_count += 1
    observation_count = len(state.observations)

    if observation_count > 0:
        average_visibility = (total_visibility / observation_count)
        stats_contents = [
            f"Total Observations: {observation_count}",
            f"Average Bortle Rating: {round(average_visibility, 2)}",
            f"Cloudy Observations: {cloudy_count}",
            f"Most Recent Object: {state.last_object_viewed}"
        ]
    else:
        stats_contents = ["No observations have been recorded."]

    return Page(state, [Header("Observation Summary")] + stats_contents + [Button("Back Home", index)])

@route
def favorites_page(state: State) -> Page:
    """Displays favorite observations."""
    fav_contents = []
    for favorite in state.favorite_objects.values():
        fav_contents.append(f"{favorite.object_name}")
        fav_contents.append(f"Type: {favorite.object_type}")
        fav_contents.append(f"Visibility: {favorite.visibility}")
        
    return Page(state, [Header("Favorite Objects")] + fav_contents + [Button("Back Home", index)])

@route
def view_log_page(state: State) -> Page:
    """Displays all entered observations."""
    log_contents = []
    if len(state.observations) == 0:
        log_contents.append("No observations have been recorded yet.")
    else:
        for obs in state.observations:
            log_contents.append(f"Object: {obs.object_name}")
            log_contents.append(f"Type: {obs.object_type}")
            log_contents.append(f"Date: {obs.date}")
            log_contents.append(f"Visibility: {obs.visibility}")
            log_contents.append(f"Cloudy: {obs.cloudy}")
            log_contents.append(f"Notes: {obs.notes}")
            log_contents.append("---")
            
    return Page(state, [Header("All Observations Logged")] + log_contents + [Button("Back Home", index)])

@route
def clear_observations(state: State) -> Page:
    """Resets all observation data."""
    state.observations = []
    state.favorite_objects = {}
    state.total_observations = 0
    state.sky_message = ("Observation log cleared.")
    state.last_object_viewed = "None"
    return index(state)

# Test 1: Index Route
assert_equal(
    index(State([], {}, 0, "Welcome!", "None")),
    Page(
        State([], {}, 0, "Welcome!", "None"),
        [
            Header("Observation Logbook"),
            "Last viewed:",
            "None",
            "Observations Logged:",
            "0",
            Button("Add Observation", "add_observation_page"),
            Button("Summary", "summary_page"),
            Button("Favorites", "favorites_page"),
            Button("Clear Log", "clear_observations"),
            Button("View Log", "view_log_page")]))

# Test 2: Add Observation Page Route
assert_equal(
    add_observation_page(State([], {}, 0, "", "None")),
    Page(
        State([], {}, 0, "", "None"),
        [
            Header("Add Observation"),
            "Object Name:",
            TextBox("object_name", ""),
            "Object Type:",
            SelectBox("object_type", ["Moon", "Planet", "Star", "Nebula", "Galaxy"]),
            "Date (e.g., YYYY-MM-DD):",
            TextBox("date", ""),
            "Visibility Rating: Bortle scale(1-9)",
            TextBox("visibility", ""),
            "Cloudy?",
            CheckBox("cloudy", False),
            "Add to Favorites?",
            CheckBox("favorite", False),
            "Notes:",
            TextArea("notes", ""),
            Button("Submit Observation", submit_observation),
            Button("Back Home", index)]))

# Test 3: Submit Observation Route
assert_equal(
    submit_observation(
        State([], {}, 0, "", "None"),
        "Jupiter",
        "Planet",
        "2026-06-06",
        "4",
        False,
        True,
        "Very bright."),
    Page(
        State(
            [Observation("Jupiter", "Planet", 4, False, "Very bright.", "2026-06-06")],
            {"Jupiter": Observation("Jupiter", "Planet", 4, False, "Very bright.", "2026-06-06")},
            1,
            "Planet observation recorded!",
            "Jupiter"),
        [
            Header("Observation Status"),
            "Planet observation recorded!",
            Button("Back Home", index)]))

# Test 4: Summary Page Route
assert_equal(
    summary_page(
        State(
            [Observation("Mars", "Planet", 3, False, "Clear", "2026-06-06")],
            {},
            1,
            "",
            "Mars")),
    Page(
        State(
            [Observation("Mars", "Planet", 3, False, "Clear", "2026-06-06")],
            {},
            1,
            "",
            "Mars"),
        [
            Header("Observation Summary"),
            "Total Observations: 1",
            "Average Bortle Rating: 3.0",
            "Cloudy Observations: 0",
            "Most Recent Object: Mars",
            Button("Back Home", index)]))

# Test 5: Favorites Page Route
assert_equal(
    favorites_page(
        State(
            [],
            {"Mars": Observation("Mars", "Planet", 3, False, "Clear", "2026-06-06")},
            1,
            "",
            "Mars")),
    Page(
        State(
            [],
            {"Mars": Observation("Mars", "Planet", 3, False, "Clear", "2026-06-06")},
            1,
            "",
            "Mars"),
        [
            Header("Favorite Objects"),
            "Mars",
            "Type: Planet",
            "Visibility: 3",
            Button("Back Home", index)]))

# Test 6: View Log Page Route
assert_equal(
    view_log_page(
        State(
            [Observation("Mars", "Planet", 3, False, "Clear", "2026-06-06")],
            {},
            1,
            "",
            "Mars")),
    Page(
        State(
            [Observation("Mars", "Planet", 3, False, "Clear", "2026-06-06")],
            {},
            1,
            "",
            "Mars"),
        [
            Header("All Observations Logged"),
            "Object: Mars",
            "Type: Planet",
            "Date: 2026-06-06",
            "Visibility: 3",
            "Cloudy: False",
            "Notes: Clear",
            "---",
            Button("Back Home", index)]))

# Test 7: Clear Observations Route
assert_equal(
    clear_observations(
        State(
            [Observation("Moon", "Moon Phase", 5, False, "Clear visibility", "2026-06-06")],
            {},
            1,
            "Saved",
            "Moon")),
    Page(
        State([], {}, 0, "Observation log cleared.", "None"),
        [
            Header("Observation Logbook"),
            "Last viewed:",
            "None",
            "Observations Logged:",
            "0",
            Button("Add Observation", "add_observation_page"),
            Button("Summary", "summary_page"),
            Button("Favorites", "favorites_page"),
            Button("Clear Log", "clear_observations"),
            Button("View Log", "view_log_page")]))

start_server(State([], {}, 0, "Welcome to the Observation Logbook", "None"))
