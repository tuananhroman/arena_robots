"""Auxiliary node for the rosnav_rl local planner: the action_server that
backs the DRLController nav2 plugin's `get_command` service client."""

from arena_bringup.substitutions import LaunchArgument
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    ld_items: list = []
    LaunchArgument.auto_append(ld_items)

    namespace = LaunchArgument('namespace')
    agent = LaunchArgument('agent', default_value='')

    action_server = Node(
        package='rosnav_rl',
        executable='action_server.py',
        name='rosnav_action_server',
        namespace=namespace.substitution,
        output='screen',
        parameters=[
            {
                'agent_name': agent.substitution,
                'namespace': namespace.substitution,
            }
        ],
    )

    return LaunchDescription([*ld_items, action_server])
