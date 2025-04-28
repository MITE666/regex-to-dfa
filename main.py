import json


precedence = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
arity = {'*': 1, '+': 1, '?': 1, '.': 2, '|': 2}


class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return '{ ' + str(self.left) + ' } ' + str(self.value) + ' { ' + str(self.right) + ' }'


class State:
    def __init__(self):
        self.transitions = {}
        self.epsilon = set()


class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class DFAState:
    def __init__(self, state_set):
        self.state_set = frozenset(state_set)
        self.transitions = {}
        self.is_final = False


def add_concat(regex_str):
    new_regex_str = ''
    prev = None
    for char in regex_str:
        if ((prev is not None and (prev.isalnum() or prev in ')*+?')) and
                (char.isalnum() or char == '(')):
            new_regex_str += '.'
        new_regex_str += char
        prev = char
    return new_regex_str


def regex_to_postfix(regex_str):
    postfix_queue = []
    stack = []
    for char in regex_str:
        if char.isalnum():
            postfix_queue.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack[-1] != '(':
                postfix_queue.append(stack.pop())
            stack.pop()
        else:
            while (stack and stack[-1] != '(' and
                   precedence[stack[-1]] >= precedence[char]):
                postfix_queue.append(stack.pop())
            stack.append(char)
    while stack:
        postfix_queue.append(stack.pop())
    return postfix_queue


def create_tree(postfix_queue):
    stack = []
    for char in postfix_queue:
        if char.isalnum():
            stack.append(Node(char))
        else:
            if arity[char] == 1:
                new_node = Node(char, stack.pop())
                stack.append(new_node)
            else:
                new_node = Node(char, stack.pop(-2), stack.pop())
                stack.append(new_node)
    return stack.pop()


def build_nfa(node):
    if node.value.isalnum():
        start = State()
        end = State()
        start.transitions[node.value] = {end}
        return NFA(start, end)
    elif node.value == '*':
        start = State()
        end = State()
        inner_nfa = build_nfa(node.left)
        start.epsilon.update([inner_nfa.start, end])
        inner_nfa.end.epsilon.update([inner_nfa.start, end])
        return NFA(start, end)
    elif node.value == '+':
        start = State()
        end = State()
        inner_nfa = build_nfa(node.left)
        start.epsilon.add(inner_nfa.start)
        inner_nfa.end.epsilon.update([inner_nfa.start, end])
        return NFA(start, end)
    elif node.value == '?':
        start = State()
        end = State()
        inner_nfa = build_nfa(node.left)
        start.epsilon.update([inner_nfa.start, end])
        inner_nfa.end.epsilon.add(end)
        return NFA(start, end)
    elif node.value == '.':
        left_nfa = build_nfa(node.left)
        right_nfa = build_nfa(node.right)
        left_nfa.end.epsilon.add(right_nfa.start)
        return NFA(left_nfa.start, right_nfa.end)
    elif node.value == '|':
        start = State()
        end = State()
        left_nfa = build_nfa(node.left)
        right_nfa = build_nfa(node.right)
        start.epsilon.update([left_nfa.start, right_nfa.start])
        left_nfa.end.epsilon.add(end)
        right_nfa.end.epsilon.add(end)
        return NFA(start, end)


def print_nfa(state, visited=None):
    if visited is None:
        visited = set()
    if state in visited:
        return
    visited.add(state)
    for symbol, targets in state.transitions.items():
        for target in targets:
            print(f"{id(state)} --{symbol}--> {id(target)}")
            print_nfa(target, visited)
    for target in state.epsilon:
        print(f"{id(state)} --ε--> {id(target)}")
        print_nfa(target, visited)


def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        current_state = stack.pop()
        for next_state in current_state.epsilon:
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure


def move(states, symbol):
    result = set()
    for state in states:
        if symbol in state.transitions:
            result.update(state.transitions[symbol])
    return result


def nfa_to_dfa(nfa, alphabet):
    initial_state = epsilon_closure({nfa.start})
    start_state = DFAState(initial_state)
    if nfa.end in initial_state:
        start_state.is_final = True

    dfa_states = {start_state.state_set: start_state}
    unprocessed = [start_state]

    while unprocessed:
        current = unprocessed.pop()
        for symbol in alphabet:
            next_set = epsilon_closure(move(current.state_set, symbol))
            if not next_set:
                continue
            next_set_frozen = frozenset(next_set)
            if next_set_frozen not in dfa_states:
                new_dfa_state = DFAState(next_set)
                if nfa.end in next_set:
                    new_dfa_state.is_final = True
                dfa_states[next_set_frozen] = new_dfa_state
                unprocessed.append(new_dfa_state)
            current.transitions[symbol] = dfa_states[next_set_frozen]

    return start_state, list(dfa_states.values())


def print_dfa(all_states):
    for state in all_states:
        print(f"State {id(state)} (final: {state.is_final})")
        for symbol, target in state.transitions.items():
            print(f"  {id(state)} --{symbol}--> {id(target)}")


def simulate_dfa(start_state, input_string):
    current_state = start_state
    for symbol in input_string:
        if symbol not in current_state.transitions:
            return False
        current_state = current_state.transitions[symbol]
    return current_state.is_final


with open('LFA-Assignment2_Regex_DFA_v2.json', 'r') as file:
    data = json.load(file)

for entry in data:
    name = entry['name']

    regex = entry['regex']
    regex_string = add_concat(regex)

    test_strings = entry['test_strings']

    postfix = regex_to_postfix(regex_string)
    root = create_tree(postfix)
    nfa = build_nfa(root)

    # print_nfa(nfa.start)

    alphabet = set()
    for c in regex_string:
        if c.isalnum():
            alphabet.add(c)

    dfa_start, all_dfa_states = nfa_to_dfa(nfa, alphabet)

    # print_dfa(all_dfa_states)

    choice = input('Type "test" for testing json\nType anything else for self-testing\n')

    print(regex)

    if choice == 'test':
        for test in test_strings:
            print(test['input'])
            print(f"Result: {simulate_dfa(dfa_start, test['input'])}, Expected: {test['expected']}")
    else:
        print('Write "exit" in order to quit\n')
        while True:
            choice = input()
            if choice == 'exit':
                break
            result = simulate_dfa(dfa_start, choice)
            print(result)