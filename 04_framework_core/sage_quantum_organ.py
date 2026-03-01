import numpy as np
import uuid
import time
import pandas as pd
import streamlit as st


class QuantumOrganTransporter:
    def __init__(self, agent_id, current_location):
        self.agent_id = agent_id
        self.current_location = current_location
        self.current_phi = np.random.uniform(0.5, 0.9)  # Historical ego strength
        self.coherence_level = 1.0
        self.state_tensor = np.random.rand(5)  # Probabilities for 5 possible routes

    def evaluate_routes(self, environmental_factors):
        """
        Simulate calculating routing options based on organ viability, traffic, weather.
        Returns a suggested route index and confidence (phi).
        """
        # Add environmental noise to routing logic
        adjusted_tensor = self.state_tensor * environmental_factors
        best_route_idx = np.argmax(adjusted_tensor)
        confidence = np.max(adjusted_tensor) / np.sum(adjusted_tensor)

        return best_route_idx, confidence


class EntangledPairResolver:
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
        self.dissonance_log = []

    def force_dissonance_resolution(self, route_a, route_b, conf_a, conf_b):
        """
        When two nodes disagree on the best route for an organ, they don't crash.
        They resolve it based on Ego Dominance (phi) and historical success.
        """
        if route_a == route_b:
            return route_a, "Coherent Agreement"

        # Dissonance Detected! Calculate dominating Ego
        effective_phi_a = self.node_a.current_phi * conf_a
        effective_phi_b = self.node_b.current_phi * conf_b

        if effective_phi_a > effective_phi_b:
            winner = route_a
            loser = route_b
            # Loser suffers a coherence penalty
            self.node_b.coherence_level -= 0.1
            dominant_node = self.node_a.agent_id
        else:
            winner = route_b
            loser = route_a
            self.node_a.coherence_level -= 0.1
            dominant_node = self.node_b.agent_id

        # The losing node's input is saved as subconscious bias for the next simulation cycle
        self.dissonance_log.append(
            {
                "timestamp": time.time(),
                "winner_route": winner,
                "loser_route": loser,
                "dominant_node": dominant_node,
            }
        )

        return winner, f"Resolved via Ego-Dominance by {dominant_node}"


def simulate_quantum_organ_transport():
    print("Initializing SAGE Quantum Organ Routing Simulation...")

    # Setup Nodes (e.g. Hospital A dispatch vs Transport Vehicle onboard computer)
    hospital_node = QuantumOrganTransporter("Hospital_Dispatch", "JFK")
    vehicle_node = QuantumOrganTransporter("Drone_C1", "Skyway_7")

    resolver = EntangledPairResolver(hospital_node, vehicle_node)

    # Environmental Data Stream (simulating a storm rolling in)
    environmental_data = [
        np.array([0.9, 0.8, 0.2, 0.5, 0.1]),  # Clear
        np.array([0.4, 0.9, 0.1, 0.2, 0.8]),  # Storm pushing East
        np.array([0.1, 0.2, 0.9, 0.8, 0.4]),  # Storm hitting central route
    ]

    results = []

    for i, env in enumerate(environmental_data):
        print(f"\n--- Condition Check {i + 1} ---")
        # Nodes independently calculate best route based on their localized tensors
        route_h, conf_h = hospital_node.evaluate_routes(env)
        route_v, conf_v = vehicle_node.evaluate_routes(
            env * np.random.uniform(0.8, 1.2, 5)
        )  # Vehicle sees slightly different data

        print(
            f"Hospital suggests Route {route_h} (Conf: {conf_h:.2f}, Ego: {hospital_node.current_phi:.2f})"
        )
        print(
            f"Vehicle suggests Route {route_v} (Conf: {conf_v:.2f}, Ego: {vehicle_node.current_phi:.2f})"
        )

        # Hardware-level Entanglement Check
        final_route, resolution_msg = resolver.force_dissonance_resolution(
            route_h, route_v, conf_h, conf_v
        )
        print(
            f"SAGE Entanglement Result: Chosen Route {final_route} ({resolution_msg})"
        )

        results.append(
            {
                "Condition": i + 1,
                "Hospital_Route": route_h,
                "Vehicle_Route": route_v,
                "Final_Route": final_route,
                "Resolution": resolution_msg,
            }
        )

    return pd.DataFrame(results)


if __name__ == "__main__":
    df_results = simulate_quantum_organ_transport()
    print("\nFinal Routing Decisions:")
    print(df_results)
