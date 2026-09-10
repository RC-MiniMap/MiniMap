# campus-navigator

> **A web app that gives step-by-step walking directions inside a university building.** Think Google Maps, but for hallways and staircases.

---

## What Are We Building?

Picture this: it's the first day of university. You found the right building, but you have no idea how to get to your classroom. You open our website, type in your classroom number and the building you're already in, and the app walks you through it step by step:

> _"Walk through the double doors. → Turn left at the staircase. → Your classroom is the second door on your right."_

Each instruction can be dismissed as you go, similar to how Google Maps lets you skip a step once you've completed it. The first version covers **one building**. The project is designed so it can grow later.

---

## Tech Stack

|Tool|What It Does|
|---|---|
|**Python**|Main programming language for backend logic|
|**Flask**|Turns our Python code into a running website|
|**NetworkX**|Models the building as a graph and calculates the shortest path between rooms|
|**HTML & CSS**|Structure and styling of the webpage|
|**Leaflet.js**|Draws the building grid, route line, and route markers|
|**JSON**|Text files that store our building data (rooms, coordinates, connections)|
|**uv**|Package manager — installs and manages Python libraries|
|**Git**|Version control — tracks changes so the team can collaborate without overwriting each other|

### How the Pathfinding Works

The building is modeled as a **graph** — locations are **nodes** and the walking paths between them are **edges**. Every node stores six things:

1. **id** — a unique identifier for the node (e.g., `"NPB_5_102"`), used to reference it in edges and routing queries
2. **name** — the human-readable label (e.g., `"5.102"` or `"Main Staircase"`), displayed in directions
3. **type** — the category of location (e.g., `"room"`, `"staircase"`, `"elevator"`, `"waypoint"`, `"spine"`). A `"spine"` node represents a main hallway/backbone connector used to route movement through the building, and the field is used to filter and categorize nodes
4. **building** — the building code (e.g., `"NPB"`), allowing multi-building support
5. **coords** — the `[x, y]` coordinates used to draw the blue route line on the map grid
6. **floor** — the floor number the node is on, allowing multi-floor pathfinding and filtering. The browser map preview supports one floor at a time; multi-floor routes still show their step-by-step directions.

Each edge stores 4 things:

1. **source** — the starting node (e.g., `"door_101"`), where the path segment begins
2. **target** — the ending node (e.g., `"hallway_corner"`), where the path segment ends
3. **weight** — the distance or "cost" of traversing this edge (e.g., `20` pixels or steps), used by the shortest-path algorithm to find the optimal route
4. **instruction** — the human-readable direction text (e.g., `"Exit Room 101 and turn RIGHT into the hallway."`), displayed to the user as a step in the directions

> Keep in mind, there are 2 edges per connection between 2 nodes, and the instructions are different based on which direction you are going.

When a user asks for directions, `NetworkX` runs a shortest-path algorithm across the graph and returns a list of nodes. From that one list, we produce both the step-by-step text directions _and_ the visual blue line — the coordinates are already stored in the nodes.

---

## Project Structure

```
campus_navigator/
│
├── .venv/                       ← Local virtual environment managed by uv
├── .python-version              ← Specifies the exact Python version for the project
├── pyproject.toml               ← The modern source of truth for dependencies and metadata
├── uv.lock                      ← The exact "locked" versions of every library for consistency
├── .gitignore                   ← Tells Git to ignore the virtual environment and cache files
│
├── run.py                       ← Start the app by running this file
├── README.md                    ← Project documentation and setup instructions
│
├── app/                         ← Everything that makes the app work lives here
│   ├── __init__.py              ← Tells Python "this folder is a package" & starts Flask
│   ├── routes.py                ← Handles URLs: connects user input → logic → webpage
│   │
│   ├── logic/                   ← The "brain" of the app (pathfinding code)
│   │   ├── __init__.py          ← Exports the navigation interface
│   │   └── navigation.py        ← Builds complete route outcomes from form input
│   │
│   ├── static/                  ← Files the browser downloads directly
│   │   ├── css/
│   │   │   └── styles.css       ← Page styling
│   │   └── js/
│   │       ├── directions.js    ← Step-by-step direction cards
│   │       └── map.js            ← Draws the route on a Leaflet grid
│   │
│   └── templates/               ← HTML pages Flask serves to the user
│       └── index.html           ← The search, directions, and map page
│
└── data/                        ← Building data — treated like a database
    ├── nodes.json               ← Every room/intersection with its name and coordinates
    └── edges.json               ← Every walking connection between two nodes
```


This structure follows the **MVC (Model–View–Controller)** pattern — each part of the app has one job and they don't mix. The practical benefit for the team is that multiple people can work on different files simultaneously without conflicting.

- **`data/`** — raw building data. Can be edited without touching any Python.
- **`app/logic/`** — pure pathfinding logic. Can be tested without running the website.
- **`app/templates/` and `app/static/`** — everything the user sees. No math here.
- **`app/routes.py`** — connects the other three. No math, no styling.

---

## How the Code Connects

```
User types "Room 101" and clicks Go
        ↓
routes.py receives the form input
        ↓
routes.py passes the form to navigation.py
        ↓
navigation.py loads map facts and runs NetworkX shortest_path()
navigation.py returns one outcome with status, directions, floors, and map-ready data
        ↓
routes.py passes that outcome to index.html (via Flask's render_template)
        ↓
index.html displays the step-by-step text directions
map.js reads the coordinates and draws the blue line over a coordinate grid
        ↓
User sees directions on screen ✓
```

---

## Team Roles

Roles can be shared — it's fine for two people to work in the same area. What matters is that everyone knows which files they own so we don't overwrite each other. If you need to touch a file outside your area, give the owner a heads up first.

### 🗂️ Data (1–2 people)

**Workspace: `data/`**

Walk the building and define the graph. Every intersection, staircase, entrance, and classroom becomes a node. Record the pixel coordinates for each by opening the floor plan image and hovering over each location to find its X/Y position. Deliverables are `nodes.json` and `edges.json` — the rest of the app depends on this data.

### ⚙️ Backend (1–2 people)

**Workspace: `app/logic/navigation.py`**

Keep route rules behind the `navigate()` interface. It loads the JSON files, builds the NetworkX graph, describes floor transitions, and decides whether the route has map-ready data. Test behavior through the complete outcome returned by `navigate()`.

### 🎨 Frontend (1–2 people)

**Workspace: `app/templates/`, `app/static/`**

Build the HTML/CSS pages and write the JavaScript that draws the animated blue line over the coordinate grid. Keep it mobile-friendly. Users will be on their phones while walking.

### 🔌 Integration (1 person)

**Workspace: `app/__init__.py`, `app/routes.py`, `run.py`**

Set up Flask and write the routes that connect the backend functions to the frontend pages. Make sure that when the form submits, the right code runs and the result shows up on screen.

---

## Git Basics

> **Git and GitHub are different things.**
> 
> - **Git** is a tool on your computer that tracks changes to files.
> - **GitHub** is a website that hosts a shared copy of the project online.

### Every Work Session

```bash
# Before you start — get your teammates' latest changes
git pull

# After finishing a chunk of work
git add .
git commit -m "describe what you did"
git push
```

### The Rules

1. **Never commit directly to `main`.** Work on your own branch and let the team leader merge it.
2. **Pull before you push.** Always `git pull` before `git push`.
3. **Write descriptive commit messages.** `"fixed stuff"` is not useful. `"Fixed bug when start and end room are the same"` is.
4. **Respect each other's files.** Communicate before editing outside your workspace.

---

## Setting Up Your Environment

> For **Windows** users — follow these steps in order.

### Step 1 — Install VSCode

Download from [https://code.visualstudio.com](https://code.visualstudio.com/). Install the **Python extension** from the Extensions tab on the left sidebar.

### Step 2 — Install Python

Download from [https://www.python.org/downloads/](https://www.python.org/downloads/). During installation, **check "Add Python to PATH"** — easy to miss, important to do.

### Step 3 — Install uv

Open the terminal in VSCode (`` Ctrl + ` ``) and run:

```bash
pip install uv
```

### Step 4 — Clone the Repository

```bash
git clone https://github.com/RC-temp-name/campus-navigator
cd campus_navigator
```

### Step 5 — Install Dependencies

```bash
uv sync
```

### Step 6 — Run the App

_(not set up yet — will update this when the server is ready)_

---

## TODO — Second Week

- [ ] **Learn how to use `uv` package manager** — [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/) (Don't have to know much, just really useful for managing python versions and dependencies, and running python files.)
- [x] **Learn how to use VSCode**
- [ ] **Keep learning Python** — [freecodecamp.org](https://www.freecodecamp.org/)
- [ ] **Learn how Git works** — [git branching game](https://learngitbranching.js.org/?locale=en_US)
- [ ] **Learn about WSL** -- Very helpful for developing on windows.
- [ ] **Learn about pull requests**

Goal for the second week is to understand more about python so we can start developing, and to understand how to work together using git branches.
Next week we will get started coding, after we are all comfortable with the tools above.

> **Note:** Git and GitHub are different. Focus on understanding `clone`, `add`, `commit`, `push`, and `pull` — those five commands cover 90% of what we'll use.
