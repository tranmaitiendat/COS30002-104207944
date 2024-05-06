class Graph:
    def __init__(self):
        self.objectives = {
            'stay healthy': 5,
            'consume food': 3,
            'be productive': 2
        }
        
        self.activities = {
            'consume junk food': {'consume food': -2, 'stay healthy': +3, 'be productive': +1},
            'work in coal mine': {'consume food': 6, 'stay healthy': +2, 'be productive': -3},
            'consume nutritious food': {'consume food': -4, 'stay healthy': -3, 'be productive': +3},
            'work as kitchen assistant with complimentary meal': {'consume food': -1, 'stay healthy': -1, 'be productive': -1}
        }

class Node:
    def __init__(self, state=None, parent=None, actions_taken=[]):
        self.state = state
        if state is None:
            graph = Graph()
            self.state = graph.objectives
        
        self.parent = parent
        self.actions_taken = actions_taken
    
    def objectives_reached(self):
        return all(value == 0 for value in self.state.values())
    
    def generate_child(self, activity):
        graph = Graph()
        new_state = {}
        
        if activity in graph.activities:
            for objective in graph.objectives:
                new_state[objective] = max(0, self.state[objective] + graph.activities[activity][objective])
            
            return Node(state=new_state, parent=self, actions_taken=self.actions_taken + [activity])
        
        return None
    
    def print_node(self):
        print("\n=====================================================================")
        print("Remaining values to reach each objective:")
        for objective, value in self.state.items():
            print(f"    - Objective {objective}: {value}")
        
        print(f"Activities performed to reach this state: {self.actions_taken}")

def bfs_search(initial_node):
    queue = [initial_node]
    visited_states = []
    
    while queue:
        current_node = queue.pop(0)
        current_node.print_node()
        visited_states.append(current_node.state)
        
        if current_node.objectives_reached():
            print("\n=====================================================================")
            print("ALL OBJECTIVES REACHED!")
            return
        
        graph = Graph()
        
        for activity in graph.activities:
            child_node = current_node.generate_child(activity)
            
            if child_node and child_node.state not in visited_states:
                queue.append(child_node)
    
    raise ValueError("No solution found!")

if __name__ == '__main__':
    graph = Graph()
    initial_node = Node()
    bfs_search(initial_node)