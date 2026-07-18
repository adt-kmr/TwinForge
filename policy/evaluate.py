"""Sim rollout + the section 11.5 validation gate.

Navigation is split the way Nav2 splits it (section 11.3): a global planner finds a
route through the navmesh, and the learned policy is the *local controller* that tracks
it. That split is why behaviour cloning is worth anything here — a policy that only ever
drives straight at the goal cannot get around a table, no matter how well it is fitted.

Observation is the vector to a lookahead point on the path; action is a capped step.
A policy only reaches hardware if it clears SIM_GATE.
"""
from collections import deque

import numpy as np

from twin.generator import is_blocked

SIM_GATE = 0.6         # minimum success rate before a policy is exportable
MAX_STEP = 0.5         # m per control tick, matching the adapters' MAX_LINEAR_SPEED
GOAL_TOLERANCE = 0.15  # m
LOOKAHEAD = 0.6        # m: how far along the path the controller aims
ROBOT_RADIUS = 0.25    # m: obstacles are inflated by this before planning
# Demonstrator gain. The expert is a proportional controller because that is a linear
# map, so a linear policy can actually represent it. Demonstrating a normalized
# direction instead (constant speed) is not linearly representable and will not train.
DEMO_GAIN = 0.3


def _cell_of(navmesh: dict, x: float, y: float) -> tuple:
    cell, (x0, y0) = navmesh["cell"], navmesh["origin"]
    return int((y - y0) / cell), int((x - x0) / cell)


def _centre_of(navmesh: dict, row: int, col: int) -> tuple:
    cell, (x0, y0) = navmesh["cell"], navmesh["origin"]
    return x0 + (col + 0.5) * cell, y0 + (row + 0.5) * cell


def free_cells(navmesh: dict) -> list:
    """Every traversable (x, y) centre in the navmesh."""
    return [
        _centre_of(navmesh, row, col)
        for row in range(navmesh["height"])
        for col in range(navmesh["width"])
        if not navmesh["grid"][row][col]
    ]


def inflate(navmesh: dict, radius: float = ROBOT_RADIUS) -> dict:
    """Grow every obstacle by the robot's radius — Nav2's costmap inflation.

    Planning on the raw grid produces paths that graze obstacles, and a controller
    aiming at a lookahead point then cuts the corner straight through them. Inflating
    first is what buys the clearance that makes corner-cutting safe.
    """
    cell, grid = navmesh["cell"], navmesh["grid"]
    height, width = navmesh["height"], navmesh["width"]
    reach = int(np.ceil(radius / cell))
    inflated = [row[:] for row in grid]

    for row in range(height):
        for col in range(width):
            if not grid[row][col]:
                continue
            for drow in range(-reach, reach + 1):
                for dcol in range(-reach, reach + 1):
                    nr, nc = row + drow, col + dcol
                    if 0 <= nr < height and 0 <= nc < width:
                        if (drow * cell) ** 2 + (dcol * cell) ** 2 <= radius ** 2:
                            inflated[nr][nc] = 1
    return {**navmesh, "grid": inflated}


def plan_path(navmesh: dict, start, goal) -> list:
    """Shortest grid route from start to goal, as a list of (x, y). Empty if unreachable.

    Breadth-first on the occupancy grid — uniform cost, so BFS already gives the
    shortest path and A*'s heuristic would only buy constant factors on a 50x50 room.
    """
    grid, height, width = navmesh["grid"], navmesh["height"], navmesh["width"]
    start_cell, goal_cell = _cell_of(navmesh, *start), _cell_of(navmesh, *goal)

    for row, col in (start_cell, goal_cell):
        if not (0 <= row < height and 0 <= col < width) or grid[row][col]:
            return []
    if start_cell == goal_cell:
        return [tuple(goal)]

    came_from: dict[tuple, tuple | None] = {start_cell: None}
    queue = deque([start_cell])
    while queue:
        row, col = queue.popleft()
        if (row, col) == goal_cell:
            break
        for drow in (-1, 0, 1):
            for dcol in (-1, 0, 1):
                if not (drow or dcol):
                    continue
                nr, nc = row + drow, col + dcol
                if not (0 <= nr < height and 0 <= nc < width) or grid[nr][nc]:
                    continue
                # Never cut a diagonal past a corner — the robot has width.
                if drow and dcol and (grid[row][nc] or grid[nr][col]):
                    continue
                if (nr, nc) not in came_from:
                    came_from[(nr, nc)] = (row, col)
                    queue.append((nr, nc))

    if goal_cell not in came_from:
        return []

    path: list = []
    node: tuple | None = goal_cell
    while node is not None:
        path.append(_centre_of(navmesh, *node))
        node = came_from[node]
    path.reverse()
    path[-1] = tuple(goal)  # finish at the exact goal, not its cell centre
    return path


def _cap(action):
    """Clamp a commanded step to the robot's actual per-tick reach."""
    norm = float(np.linalg.norm(action))
    return action * (MAX_STEP / norm) if norm > MAX_STEP else action


def _lookahead(path: list, pos, index: int) -> tuple:
    """Advance along the path to a point ~LOOKAHEAD ahead; returns (target, index)."""
    while index < len(path) - 1 and np.linalg.norm(np.asarray(path[index]) - pos) < LOOKAHEAD:
        index += 1
    return np.asarray(path[index], dtype=np.float64), index


def rollout(policy, navmesh: dict, goal, start, max_steps: int = 200,
            planning_mesh: dict | None = None) -> bool:
    """One episode; True if the goal was reached without hitting anything.

    Planning uses the inflated grid; collision checks use the real one.
    """
    goal = np.asarray(goal, dtype=np.float64)
    path = plan_path(planning_mesh or inflate(navmesh), start, goal)
    if not path:
        return False

    pos = np.asarray(start, dtype=np.float64)
    index = 0
    for _ in range(max_steps):
        if np.linalg.norm(goal - pos) <= GOAL_TOLERANCE:
            return True
        target, index = _lookahead(path, pos, index)
        pos = pos + _cap(np.asarray(policy.act(target - pos), dtype=np.float64))
        if is_blocked(navmesh, pos[0], pos[1]):
            return False
    return bool(np.linalg.norm(goal - pos) <= GOAL_TOLERANCE)


def record_demos(navmesh: dict, goal, n: int = 10, max_steps: int = 200, seed: int = 0):
    """Teleop-style demonstrations: proportional control tracking the planned path.

    Demos that would drive through an obstacle are dropped rather than recorded — a
    demonstration of a collision is worse than no demonstration.
    """
    rng = np.random.default_rng(seed)
    planning_mesh = inflate(navmesh)
    cells = free_cells(planning_mesh)  # only start where a robot actually fits
    goal = np.asarray(goal, dtype=np.float64)
    demos: list = []
    if not cells:
        return demos

    for start_idx in rng.choice(len(cells), size=min(n, len(cells)), replace=False):
        start = cells[start_idx]
        path = plan_path(planning_mesh, start, goal)
        if not path:
            continue

        pos = np.asarray(start, dtype=np.float64)
        obs, actions, index, ok = [], [], 0, False
        for _ in range(max_steps):
            if np.linalg.norm(goal - pos) <= GOAL_TOLERANCE:
                ok = True
                break
            target, index = _lookahead(path, pos, index)
            delta = target - pos
            action = _cap(DEMO_GAIN * delta)
            obs.append(delta.copy())
            actions.append(action.copy())
            pos = pos + action
            if is_blocked(navmesh, pos[0], pos[1]):
                break
        if ok and obs:
            demos.append({"obs": np.array(obs), "actions": np.array(actions)})
    return demos


def evaluate(policy, navmesh: dict, goal, episodes: int = 20, max_steps: int = 200,
             seed: int = 1) -> dict:
    """Success rate over randomly-started episodes — the gate's input."""
    rng = np.random.default_rng(seed)
    planning_mesh = inflate(navmesh)
    cells = free_cells(planning_mesh)
    if not cells:
        return {"success_rate": 0.0, "episodes": 0, "passed": False}

    starts = rng.choice(len(cells), size=episodes, replace=len(cells) < episodes)
    successes = sum(
        rollout(policy, navmesh, goal, cells[i], max_steps, planning_mesh)
        for i in starts
    )
    rate = successes / episodes
    return {"success_rate": rate, "episodes": episodes, "passed": rate >= SIM_GATE}
