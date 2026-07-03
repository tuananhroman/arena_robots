# Bringup adapter launch files

This directory contains per-bringup-kind launch files. They are implementation
details of `arena_robots.bringup.*` classes — not public entry points.

The public entry point is [`launch/bringup.launch.py`](../bringup.launch.py).
Users invoke that file; it selects and includes the appropriate file here based
on the `bringup` argument.

## Files

### `nav2.launch.py`

Internals of `arena_robots.bringup.nav2.Nav2Bringup`. Instantiates a full nav2
stack (map server, AMCL, planner, controller, bt_navigator, lifecycle manager)
in the given namespace. Accepts launch arguments for planner selection
(`global_planner`, `local_planner`, `inter_planner`), sim time, costmap frame,
and an optional `task_generator_node` name for map topic remapping (empty
string = no remap, which is the standalone default). The companion
`env_namespace` arg (the env-root namespace, e.g. `/arena/env_0`) is
plumbed through identically and is used for env-intrinsic topics that do
not live under `task_generator_node`, such as `door_mask` for
`nav2_mask_overlay_layer`. Planner selection is
typically driven from
[cap-scoped overrides](../../../../arena_bringup/BRINGUP.md#cap-scoped-overrides)
at launch (`mobile.local_planner:=teb`, etc.) which the task-generator
forwards to this launch file.

### `rosnav_rl.launch.py`

Internals of `arena_robots.bringup.mobile.rosnav_rl.RosnavRlBringup`. Starts a
single `rosnav_rl` inference node (`arena_inference_node.py`) that publishes
`cmd_vel` directly — no nav2 stack. Selected via `mobile:=rosnav_rl
mobile.agent:=<agent>`, where `<agent>` names a directory under
`arena_training/agents/` (either SB3 or DreamerV3 backend — both load through
`RL_Agent.from_agent_dir()`, see the
[rosnav_rl README](../../../../arena_training/deps/rosnav_rl/rosnav_rl/README.md#deploy-a-pre-trained-agent)).

The same agent is also reachable behind nav2 via `mobile:=nav2
mobile.local_planner:=rosnav_rl` — that route uses the native `nav2.launch.py`
below plus the `rosnav_rl` controller's
[`controller.launch.py` side-car](../../config/nav2/controllers/rosnav_rl/controller.launch.py),
which starts the `action_server.py` node backing the `DRLController` nav2
plugin's `get_command` service. Both routes accept the bare-name shorthand
`planner:=<agent>` (resolved by `arena_planners`' resolver, which discovers
agents under `arena_training/agents/` the same way).

### `none.launch.py`

Internals of `arena_robots.bringup.none.NoneBringup`. Spins up no navigation
stack. The `task_server` will publish goals directly to a goal-pose topic.
Use this for robots driven by an external planner that subscribes to a goal
topic.

## Adding a new bringup kind

Create `<kind>.launch.py` here, then add a `Bringup` subclass in
`arena_robots/arena_robots/arena_robots/bringup/<cap>/<kind>.py` whose
`_launch_actions()` includes this file. Implement handlers under
`arena_robots/arena_robots/arena_robots/task_server_handlers/<task_kind>/`
and declare them on the `Bringup` subclass via a `task_handlers: ClassVar`
mapping `TaskKind` to a zero-arg loader function. The `task_server` reads
that mapping directly, no central registry to update.
