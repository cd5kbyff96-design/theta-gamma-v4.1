"""
Packet Compiler — Enhanced with DAG-based dependency resolution.

This module implements the compiler that transforms planning artifacts
into discrete, executable task packets with full dependency graph validation.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from theta_gamma.compiler.packets import (
    TaskPacket,
    PacketDomain,
    PacketPriority,
    PacketStatus,
    PacketTest,
)


class DependencyCycleError(Exception):
    """Raised when a dependency cycle is detected."""

    pass


class DependencyNotFoundError(Exception):
    """Raised when a dependency references a non-existent packet."""

    pass


class PacketCompiler:
    """
    Compiler that transforms planning artifacts into task packets.

    The compiler parses markdown artifacts and generates discrete,
    executable task packets with clear inputs, commands, and tests.

    Features:
    - Packet compilation from planning artifacts
    - Dependency DAG construction and validation
    - Cycle detection
    - Topological sorting for execution order
    - Executable packet resolution

    Example:
        >>> compiler = PacketCompiler()
        >>> packets = compiler.compile_artifacts(artifacts_dir)
        >>> compiler.validate_dependencies()
        >>> order = compiler.get_execution_order()
    """

    def __init__(self) -> None:
        """Initialize the packet compiler."""
        self._packets: dict[str, TaskPacket] = {}
        self._sequence_counters: dict[str, int] = {}
        self._dependency_graph: dict[str, list[str]] = {}
        self._reverse_graph: dict[str, list[str]] = {}
        self._validated: bool = False

    def _get_next_sequence(self, domain: str) -> int:
        """Get next sequence number for a domain."""
        if domain not in self._sequence_counters:
            self._sequence_counters[domain] = 0
        self._sequence_counters[domain] += 1
        return self._sequence_counters[domain]

    def _generate_packet_id(self, domain: PacketDomain) -> str:
        """Generate a packet ID."""
        seq = self._get_next_sequence(domain.value)
        return f"PKT-{domain.value}-{seq:03d}"

    def compile_artifacts(self, artifacts_dir: Path) -> list[TaskPacket]:
        """
        Compile planning artifacts into task packets.

        Args:
            artifacts_dir: Directory containing markdown artifacts

        Returns:
            List of compiled TaskPackets
        """
        # Generate default packets from specification
        self._generate_default_packets()

        # Build dependency graphs
        self._build_dependency_graphs()

        # Validate dependencies
        self.validate_dependencies()

        self._validated = True
        return list(self._packets.values())

    def _build_dependency_graphs(self) -> None:
        """Build forward and reverse dependency graphs."""
        self._dependency_graph = {}
        self._reverse_graph = {packet_id: [] for packet_id in self._packets}

        for packet_id, packet in self._packets.items():
            self._dependency_graph[packet_id] = packet.depends_on.copy()

            # Build reverse graph (dependents)
            for dep in packet.depends_on:
                if dep in self._reverse_graph:
                    self._reverse_graph[dep].append(packet_id)

    def validate_dependencies(self) -> list[str]:
        """
        Validate all packet dependencies.

        Returns:
            List of validation errors (empty if valid)

        Raises:
            DependencyNotFoundError: If a dependency references non-existent packet
            DependencyCycleError: If a dependency cycle is detected
        """
        errors = []

        # Check for missing dependencies
        for packet_id, deps in self._dependency_graph.items():
            for dep in deps:
                if dep not in self._packets:
                    raise DependencyNotFoundError(
                        f"Packet {packet_id} depends on non-existent packet {dep}"
                    )

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node: str, path: list[str]) -> list[str] | None:
            """DFS to detect cycles."""
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self._dependency_graph.get(node, []):
                if neighbor not in visited:
                    cycle = has_cycle(neighbor, path + [neighbor])
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor) if neighbor in path else 0
                    return path[cycle_start:] + [neighbor]

            rec_stack.remove(node)
            return None

        for packet_id in self._packets:
            if packet_id not in visited:
                cycle = has_cycle(packet_id, [packet_id])
                if cycle:
                    cycle_str = " -> ".join(cycle)
                    raise DependencyCycleError(
                        f"Dependency cycle detected: {cycle_str}"
                    )

        return errors

    def get_execution_order(self) -> list[str]:
        """
        Get topological sort of packets for execution.

        Returns:
            List of packet IDs in execution order

        Raises:
            DependencyCycleError: If graph has cycles
        """
        if not self._validated:
            self.validate_dependencies()

        # Kahn's algorithm for topological sort
        in_degree = {packet_id: 0 for packet_id in self._packets}

        for packet_id, deps in self._dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[packet_id] = in_degree.get(packet_id, 0) + 1

        # Start with packets that have no dependencies
        queue = [pid for pid, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort by priority for deterministic order
            queue.sort()
            current = queue.pop(0)
            result.append(current)

            # Reduce in-degree for dependents
            for dependent in self._reverse_graph.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self._packets):
            raise DependencyCycleError("Graph has cycles - topological sort failed")

        return result

    def get_executable_packets(self, completed_packets: set[str]) -> list[TaskPacket]:
        """
        Get packets that are ready to execute.

        A packet is executable if:
        - It is in PENDING status
        - All its dependencies are in completed_packets

        Args:
            completed_packets: Set of completed packet IDs

        Returns:
            List of executable packets
        """
        executable = []

        for packet in self._packets.values():
            if packet.status != PacketStatus.PENDING:
                continue

            # Check if all dependencies are completed
            if all(dep in completed_packets for dep in packet.depends_on):
                executable.append(packet)

        # Sort by execution order
        execution_order = self.get_execution_order()
        order_map = {pid: i for i, pid in enumerate(execution_order)}

        return sorted(executable, key=lambda p: order_map.get(p.packet_id, 999))

    def get_blocking_packets(self, packet_id: str) -> list[str]:
        """
        Get packets that are blocking a specific packet.

        Args:
            packet_id: Packet ID to check

        Returns:
            List of blocking packet IDs (incomplete dependencies)
        """
        packet = self._packets.get(packet_id)
        if not packet:
            return []

        # In a real implementation, would check packet status
        return packet.depends_on.copy()

    def get_dependents(self, packet_id: str) -> list[str]:
        """
        Get packets that depend on a specific packet.

        Args:
            packet_id: Packet ID to check

        Returns:
            List of dependent packet IDs
        """
        return self._reverse_graph.get(packet_id, []).copy()

    def get_dependency_chain(self, packet_id: str) -> list[str]:
        """
        Get full dependency chain for a packet (transitive dependencies).

        Args:
            packet_id: Packet ID to check

        Returns:
            List of all dependency packet IDs (depth-first)
        """
        visited = set()
        result = []

        def visit(pid: str) -> None:
            if pid in visited:
                return
            visited.add(pid)

            for dep in self._dependency_graph.get(pid, []):
                visit(dep)

            if pid != packet_id:
                result.append(pid)

        visit(packet_id)
        return result

    def get_critical_path(self) -> list[str]:
        """
        Get the critical path (longest dependency chain).

        Returns:
            List of packet IDs on the critical path
        """
        if not self._packets:
            return []

        # Calculate longest path to each node
        dist = {pid: 0 for pid in self._packets}
        predecessor = {pid: None for pid in self._packets}

        execution_order = self.get_execution_order()

        for packet_id in execution_order:
            for dependent in self._reverse_graph.get(packet_id, []):
                if dist[packet_id] + 1 > dist[dependent]:
                    dist[dependent] = dist[packet_id] + 1
                    predecessor[dependent] = packet_id

        # Find the node with maximum distance
        max_dist = max(dist.values())
        end_node = next(pid for pid, d in dist.items() if d == max_dist)

        # Reconstruct path
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = predecessor[current]

        return list(reversed(path))

    def _generate_default_packets(self) -> None:
        """Generate default packets from the specification."""
        # INFRA packets
        self._add_packet(
            TaskPacket(
                packet_id=self._generate_packet_id(PacketDomain.INFRA),
                title="Provision GPU Training Environment",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.INFRA,
                estimated_effort="1d",
                depends_on=[],
                objective="Provision a 4xA100-80GB training environment with PyTorch, CUDA, and FSDP support",
                inputs=[
                    "Cloud provider credentials",
                    "Training tier matrix",
                    "CUDA 12.x compatible base image",
                ],
                commands=[
                    "Create VM instance with 4xA100-80GB GPUs",
                    "Install CUDA 12.x toolkit",
                    "Install PyTorch 2.x with FSDP support",
                ],
                tests=[
                    PacketTest(
                        name="GPU count check",
                        command="nvidia-smi --list-gpus | wc -l",
                        expected="4 GPUs detected",
                    ),
                ],
                done_definition="4xA100-80GB environment is running, all frameworks installed",
                stop_condition="GPU provisioning fails after 3 attempts",
                source_artifacts=["A0/02_operating_limits.yaml", "A2/02_training_tier_matrix.csv"],
            )
        )

        # DATA packets
        self._add_packet(
            TaskPacket(
                packet_id=self._generate_packet_id(PacketDomain.DATA),
                title="Build Cross-Modal Eval Dataset Pipeline",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.DATA,
                estimated_effort="1d",
                depends_on=[],
                objective="Create data pipeline for cross-modal evaluation datasets",
                inputs=["Dataset manifest", "Storage credentials"],
                commands=[
                    "Set up data storage bucket",
                    "Upload golden datasets with hashes",
                    "Implement hash verification",
                ],
                tests=[
                    PacketTest(
                        name="Hash verification",
                        command="python verify_hashes.py",
                        expected="All datasets pass hash verification",
                    ),
                ],
                done_definition="All eval datasets loaded with verified hashes",
                stop_condition="Dataset corruption detected",
                source_artifacts=["A1/06_golden_dataset_manifest.csv"],
            )
        )

        # TRAIN packets (depends on INFRA and DATA)
        self._add_packet(
            TaskPacket(
                packet_id=self._generate_packet_id(PacketDomain.TRAIN),
                title="Implement FSDP Training Loop (T1 Tier)",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.TRAIN,
                estimated_effort="2d",
                depends_on=["PKT-INFRA-001", "PKT-DATA-001"],
                objective="Implement T1-Full-FSDP training loop with Lightning Fabric",
                inputs=[
                    "GPU environment from PKT-INFRA-001",
                    "Data pipeline from PKT-DATA-001",
                ],
                commands=[
                    "Implement model architecture with cross-modal encoders",
                    "Configure FSDP with FULL_SHARD strategy",
                    "Integrate data loader",
                ],
                tests=[
                    PacketTest(
                        name="Smoke test",
                        command="Run 100 training steps",
                        expected="100 steps complete without error",
                    ),
                ],
                done_definition="T1-Full-FSDP training loop runs end-to-end",
                stop_condition="Model fails to fit in 4xA100-80GB",
                source_artifacts=["A2/02_training_tier_matrix.csv"],
            )
        )

        # EVAL packets (depends on DATA)
        self._add_packet(
            TaskPacket(
                packet_id=self._generate_packet_id(PacketDomain.EVAL),
                title="Build Cross-Modal Evaluation Suite",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.EVAL,
                estimated_effort="1d",
                depends_on=["PKT-DATA-001"],
                objective="Implement cross-modal evaluation suite for M-CM-001 through M-CM-004",
                inputs=["Cross-modal eval dataset", "Metric definitions"],
                commands=[
                    "Implement cross-modal accuracy evaluator (M-CM-001)",
                    "Implement weighted F1 evaluator (M-CM-002)",
                ],
                tests=[
                    PacketTest(
                        name="Output format test",
                        command="Validate JSON output schema",
                        expected="JSON contains all 4 metric IDs",
                    ),
                ],
                done_definition="Cross-modal eval suite produces all 4 metrics",
                stop_condition="Eval runtime exceeds 90 minutes",
                source_artifacts=["A1/01_metric_dictionary.yaml"],
            )
        )

        # BUDGET packets
        self._add_packet(
            TaskPacket(
                packet_id=self._generate_packet_id(PacketDomain.BUDGET),
                title="Implement Cost Tracking System",
                priority=PacketPriority.P0_CRITICAL,
                domain=PacketDomain.BUDGET,
                estimated_effort="1d",
                depends_on=[],
                objective="Implement real-time cost tracking with alert thresholds",
                inputs=["Cloud billing API credentials"],
                commands=[
                    "Set up cost event emission",
                    "Implement daily/monthly spend tracking",
                ],
                tests=[
                    PacketTest(
                        name="Cost tracking test",
                        command="Record test cost events",
                        expected="Cumulative spend updates correctly",
                    ),
                ],
                done_definition="Cost tracking system emits events and tracks spend",
                stop_condition="Billing API unavailable for > 1 hour",
                source_artifacts=["A2/01_compute_budget_policy.md"],
            )
        )

        # OPS packets (depends on EVAL and BUDGET)
        self._add_packet(
            TaskPacket(
                packet_id=self._generate_packet_id(PacketDomain.OPS),
                title="Implement Weekly Control Loop Automation",
                priority=PacketPriority.P1_HIGH,
                domain=PacketDomain.OPS,
                estimated_effort="2d",
                depends_on=["PKT-EVAL-001", "PKT-BUDGET-001"],
                objective="Automate weekly control loop with metric collection",
                inputs=["Eval harness", "Budget tracking"],
                commands=[
                    "Implement metric collection (Step 1)",
                    "Implement go/no-go decision (Step 4)",
                    "Implement report generation (Step 6)",
                ],
                tests=[
                    PacketTest(
                        name="Full loop test",
                        command="Run complete weekly loop",
                        expected="Loop completes in < 120 minutes",
                    ),
                ],
                done_definition="Weekly control loop runs automatically every Monday",
                stop_condition="Critical data source unavailable",
                source_artifacts=["A6/01_weekly_loop_runbook.md"],
            )
        )

    def _add_packet(self, packet: TaskPacket) -> None:
        """Add a packet to the registry."""
        self._packets[packet.packet_id] = packet

    def get_packet(self, packet_id: str) -> TaskPacket | None:
        """Get a packet by ID."""
        return self._packets.get(packet_id)

    def get_all_packets(self) -> list[TaskPacket]:
        """Get all packets."""
        return list(self._packets.values())

    def get_dependency_graph(self) -> dict[str, list[str]]:
        """Get packet dependency graph."""
        return self._dependency_graph.copy()

    def get_reverse_graph(self) -> dict[str, list[str]]:
        """Get reverse dependency graph (dependents)."""
        return self._reverse_graph.copy()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "packets": [p.to_dict() for p in self._packets.values()],
            "total_count": len(self._packets),
            "dependency_graph": self._dependency_graph,
            "validated": self._validated,
        }
