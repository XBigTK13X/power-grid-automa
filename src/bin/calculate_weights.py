import sys
import os
import heapq
import pprint
import importlib


def compute_board_weights(board_definition):
    cities = [city[1] for city in board_definition["cities"]]
    adjacency = {city_name: [] for city_name in cities}

    for connection in board_definition["connections"]:
        start_city = connection[0]
        end_city = connection[2]
        cost = int(connection[3])
        adjacency[start_city].append((end_city, cost))
        adjacency[end_city].append((start_city, cost))

    all_pairs_weights = {}

    for start_city in cities:
        distances = {city: float("inf") for city in cities}
        distances[start_city] = 0
        priority_queue = [(0, start_city)]

        while len(priority_queue) > 0:
            current_dist, current_node = heapq.heappop(priority_queue)

            if current_dist > distances[current_node]:
                continue

            for neighbor, weight in adjacency[current_node]:
                dist = current_dist + weight
                if dist < distances[neighbor]:
                    distances[neighbor] = dist
                    heapq.heappush(priority_queue, (dist, neighbor))

        all_pairs_weights[start_city] = {
            target_city: distances[target_city]
            for target_city in cities
            if distances[target_city] != float("inf")
        }

    return all_pairs_weights


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python bin/calc_weights.py <module_path> <board_variable_name>")
        print("Example: python bin/calc_weights.py board.germany germany")
        print(
            "Example: python bin/calc_weights.py board.united_states_of_america united_states_of_america"
        )
        sys.exit(1)

    module_name = sys.argv[1]
    board_var_name = sys.argv[2]

    try:
        imported_module = importlib.import_module(module_name)
        board_data = getattr(imported_module, board_var_name)
    except (ImportError, AttributeError) as exc:
        print(f"Error loading board '{board_var_name}' from '{module_name}': {exc}")
        sys.exit(1)

    weights_dict = compute_board_weights(board_data)

    source_file_path = imported_module.__file__
    module_dir = os.path.dirname(source_file_path)
    base_file_name = os.path.splitext(os.path.basename(source_file_path))[0]
    output_file_path = os.path.join(module_dir, f"{base_file_name}_weights.py")

    var_name = f"{board_var_name}_weights"

    with open(output_file_path, "w") as write_handle:
        formatted_weights = pprint.pformat(weights_dict, indent=4, width=100)
        write_handle.write(f"{var_name} = {formatted_weights}\n")

    print(f"Weights successfully written to: {output_file_path}")
