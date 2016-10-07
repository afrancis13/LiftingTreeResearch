import numpy as np
import scipy.stats

import matplotlib.pyplot as plt

class BinaryIncreasingTree(object):

    # Start with a tree with root labeled 1.
    num_nodes = 1

    # Also store all nodes in the tree in a class variable.
    nodes = []

    # The construction is recursive.

    def __init__(self, label=1):
        self.labels = [label]
        self.left = None
        self.right = None
        BinaryIncreasingTree.nodes.append(self)

    def collect_labels(self):
        # DFS
        stack = [self]
        labels = []
        while len(stack) != 0:
            node = stack.pop()
            labels.append(sorted(node.labels))
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        return labels

    def get_outdegree(self):
        if self.left is None and self.right is None:
            return 0
        elif self.left is None or self.right is None:
            return 1
        return 2

    def pick_random(self):
        # Pick a node at random from the set of nodes using the rule above.
        # Insert 2 - outdegree number of nodes into the 'weighted node list'.
        # Then choose at random from this list.

        weighted_node_list = []
        for node in BinaryIncreasingTree.nodes:
            for i in range(2 - node.get_outdegree()):
                weighted_node_list.append(node)

        return weighted_node_list[np.random.randint(len(weighted_node_list))]

    def insert(self):
        node = self.pick_random()
        node.insert_node()

    def insert_node(self):
        # Insert into tree.

        new_node_label = BinaryIncreasingTree.num_nodes + 1
        BinaryIncreasingTree.num_nodes += 1

        new_node = BinaryIncreasingTree(new_node_label)

        if self.left is None and self.right is None:
            rand = np.random.randint(2)
            if rand == 0:
                self.left = new_node
            else:
                self.right = new_node
        elif self.left is None:
            self.left = new_node
        else:
            self.right = new_node

    def lift(self):
        # Lift the tree using the procedure described in the paper.
        # This requires some more complicated concepts from probability.

        # For each node, wait Exp(d+(v)) time.

        filtered_nodes = filter(lambda x: x.get_outdegree() > 0, BinaryIncreasingTree.nodes)
        node_wait_times = map(lambda x: x.get_outdegree(), BinaryIncreasingTree.nodes)
        filtered_node_wait_times = filter(lambda x: x > 0, node_wait_times)

        exp_random_draw = np.random.exponential(np.array(filtered_node_wait_times))

        min_wait_time = float("inf")
        min_wait_node = None
        for i in range(len(exp_random_draw)):
            this_wait_time = exp_random_draw[i]
            if this_wait_time < min_wait_time:
                min_wait_time = this_wait_time
                min_wait_node = filtered_nodes[i]

        # Now, perform the lifting procedure on said node.

        lifted_left = True

        if min_wait_node.left is not None and min_wait_node.right is not None:
            rand = np.random.randint(2)
            if rand == 0:
                stack = [min_wait_node.left]
            else:
                stack = [min_wait_node.right]
                lifted_left = False
        elif min_wait_node.left is not None:
            stack = [min_wait_node.left]
        elif min_wait_node.right is not None:
            stack = [min_wait_node.right]
            lifted_left = False
        else:
            raise ValueError("Node should have outdegree > 0!")

        # DFS to collect the labels.
        subtree_labels = []
        while len(stack) != 0:
            node = stack.pop()
            subtree_labels.append(node.labels)
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)

        # Remove subtree.
        if lifted_left:
            min_wait_node.left = None
        else:
            min_wait_node.right = None

        min_wait_node.labels.extend([label for sublist in subtree_labels for label in sublist])

        return min_wait_time

    def __str__(self):
        printed_tree = ""
        stack = [(self, 0)]
        # DFS
        while len(stack) != 0:
            node, depth = stack.pop()
            printed_tree += "%s>%s\n" % ("-" * depth, str(node.labels))
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))

        return printed_tree

# Script

# Number of nodes in the tree.
n = 10

# Specific resulting sets of various sizes.

result_two_timer = 0
result_two_times = []
result_two_set = [[1], [2], [3], [4], [5], [6], [8], [9], [7, 10]]

result_three_timer = 0
result_three_times = []
result_three_set = [[1], [2], [3], [4], [6], [8], [9], [5, 7, 10]]

result_four_timer = 0
result_four_times = []
result_four_set = [[2], [3], [5], [6], [7], [8], [1, 4, 9, 10]]

result_five_timer = 0
result_five_times = []
result_five_set = [[1], [4], [5], [6], [10], [2, 3, 7, 8, 9]]

result_six_timer = 0
result_six_times = []
result_six_set = [[1], [2], [5], [10], [3, 4, 6, 7, 8, 9]]

result_seven_timer = 0
result_seven_times = []
result_seven_set = [[2], [3], [6], [1, 4, 5, 7, 8, 9, 10]]

result_eight_timer = 0
result_eight_times = []
result_eight_set = [[2], [5], [1, 3, 4, 6, 7, 8, 9, 10]]

result_nine_timer = 0
result_nine_times = []
result_nine_set = [[3], [1, 2, 4, 5, 6, 7, 8, 9, 10]]

result_ten_timer = 0
result_ten_times = []
result_ten_set = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]

# Run simulations.

num_iterations = 1000000
for i in range(num_iterations):
    bit = BinaryIncreasingTree()
    for _ in range(n - 1):
        bit.insert()

    if i % 1000 == 0:
       print "Before lifting, tree is:\n"
       print bit

    time_to_lift = bit.lift()

    if i % 1000 == 0:
       print "After lifting, tree is:\n"
       print bit
       print "Finished simulation %d" % i

    resulting_labels = bit.collect_labels()

    sorted_resulting_labels = sorted(resulting_labels)

    if sorted_resulting_labels == sorted(result_two_set):
        result_two_times.append(result_two_timer)
        result_two_timer = 0
    elif sorted_resulting_labels == sorted(result_three_set):
        result_three_times.append(result_three_timer)
        result_three_timer = 0
    elif sorted_resulting_labels == sorted(result_four_set):
        result_four_times.append(result_four_timer)
        result_four_timer = 0
    elif sorted_resulting_labels == sorted(result_five_set):
        result_five_times.append(result_five_timer)
        result_five_timer = 0
    elif sorted_resulting_labels == sorted(result_six_set):
        result_six_times.append(result_six_timer)
        result_six_timer = 0
    elif sorted_resulting_labels == sorted(result_seven_set):
        result_seven_times.append(result_seven_timer)
        result_seven_timer = 0
    elif sorted_resulting_labels == sorted(result_eight_set):
        result_eight_times.append(result_eight_timer)
        result_eight_timer = 0
    elif sorted_resulting_labels == sorted(result_nine_set):
        result_nine_times.append(result_nine_timer)
        result_nine_timer = 0
    elif sorted_resulting_labels == sorted(result_ten_set):
        result_ten_times.append(result_ten_timer)
        result_ten_timer = 0

    result_two_timer += time_to_lift
    result_three_timer += time_to_lift
    result_four_timer += time_to_lift
    result_five_timer += time_to_lift
    result_six_timer += time_to_lift
    result_seven_timer += time_to_lift
    result_eight_timer += time_to_lift
    result_nine_timer += time_to_lift
    result_ten_timer += time_to_lift

    # Excuse this hack. Tried to put this in a __del__ method,
    # but was not as easy as I had hoped.

    # TODO: Better garbage collection, stop using class variables?

    BinaryIncreasingTree.num_nodes = 1
    BinaryIncreasingTree.nodes = []

def compute_theoretical_rate(n, k):
    # From the paper, assuming a = 2, b = 2.
    return (float(n + 1) / float(3)) * (scipy.special.beta(k, n - k + 2) / scipy.special.beta(2, 2))

plt.close('all')

# Plot results and overlay exponential distribution.
fig, axarr = plt.subplots(3, 3)

fig.suptitle("Theoretical vs. Empirical Lifting Distribution")

rate_two = compute_theoretical_rate(n, 2)
print("The rate for k = 2 is %.6f" % rate_two)

scale_two = 1 / rate_two

x_two = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_two),
    scipy.stats.expon.ppf(0.999, scale=scale_two),
    1000
)

axarr[0, 0].plot(x_two, scipy.stats.expon.pdf(x_two, scale=scale_two), 'r-', lw=2)
axarr[0, 0].set_xlim(0, 50)
axarr[0, 0].set_ylim(0, 0.10)
axarr[0, 0].set_title('b = 10, k = 2')
axarr[0, 0].hist(result_two_times, normed=True)

rate_three = compute_theoretical_rate(n, 3)
print("The rate for k = 3 is %.6f" % rate_three)

scale_three = 1 / rate_three

x_three = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_three),
    scipy.stats.expon.ppf(0.999, scale=scale_three),
    1000
)

axarr[0, 1].plot(x_three, scipy.stats.expon.pdf(x_three, scale=scale_three), 'r-', lw=2)
axarr[0, 1].set_xlim(0, 200)
axarr[0, 1].set_ylim(0, 0.015)
axarr[0, 1].set_title('b = 10, k = 3')
axarr[0, 1].hist(result_three_times, normed=True)

rate_four = compute_theoretical_rate(n, 4)
print("The rate for k = 4 is %.6f" % rate_four)

scale_four = 1 / rate_four

x_four = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_four),
    scipy.stats.expon.ppf(0.999, scale=scale_four),
    1000
)

axarr[0, 2].plot(x_four, scipy.stats.expon.pdf(x_four, scale=scale_four), 'r-', lw=2)
axarr[0, 2].set_xlim(0, 10000)
axarr[0, 2].set_ylim(0, 0.001)
axarr[0, 2].set_title('b = 10, k = 4')
axarr[0, 2].hist(result_four_times, normed=True)

rate_five = compute_theoretical_rate(n, 5)
print("The rate for k = 5 is %.6f" % rate_five)

scale_five = 1 / rate_five

x_five = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_five),
    scipy.stats.expon.ppf(0.999, scale=scale_five),
    1000
)

axarr[1, 0].plot(x_five, scipy.stats.expon.pdf(x_five, scale=scale_five), 'r-', lw=2)
axarr[1, 0].set_xlim(0, 5000)
axarr[1, 0].set_ylim(0, 0.001)
axarr[1, 0].set_title('b = 10, k = 5')
axarr[1, 0].hist(result_five_times, normed=True)

rate_six = compute_theoretical_rate(n, 6)
print("The rate for k = 6 is %.6f" % rate_six)

scale_six = 1 / rate_six

x_six = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_six),
    scipy.stats.expon.ppf(0.999, scale=scale_six),
    1000
)

axarr[1, 1].plot(x_six, scipy.stats.expon.pdf(x_six, scale=scale_six), 'r-', lw=2)
axarr[1, 1].set_xlim(0, 3000)
axarr[1, 1].set_ylim(0, 0.001)
axarr[1, 1].set_title('b = 10, k = 6')
axarr[1, 1].hist(result_six_times, normed=True)

rate_seven = compute_theoretical_rate(n, 7)
print("The rate for k = 7 is %.6f" % rate_seven)

scale_seven = 1 / rate_seven

x_seven = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_seven),
    scipy.stats.expon.ppf(0.999, scale=scale_seven),
    1000
)

axarr[1, 2].plot(x_seven, scipy.stats.expon.pdf(x_seven, scale=scale_seven), 'r-', lw=2)
axarr[1, 2].set_xlim(0, 10000)
axarr[1, 2].set_ylim(0, 0.001)
axarr[1, 2].set_title('b = 10, k = 7')
axarr[1, 2].hist(result_seven_times, normed=True)

rate_eight = compute_theoretical_rate(n, 8)
print("The rate for k = 8 is %.6f" % rate_eight)

scale_eight = 1 / rate_eight

x_eight = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_eight),
    scipy.stats.expon.ppf(0.999, scale=scale_eight),
    1000
)

axarr[2, 0].plot(x_eight, scipy.stats.expon.pdf(x_eight, scale=scale_eight), 'r-', lw=2)
axarr[2, 0].set_xlim(0, 7000)
axarr[2, 0].set_ylim(0, 0.001)
axarr[2, 0].set_title('b = 10, k = 8')
axarr[2, 0].hist(result_eight_times, normed=True)

rate_nine = compute_theoretical_rate(n, 8)
print("The rate for k = 9 is %.6f" % rate_nine)

scale_nine = 1 / rate_nine

x_nine = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_nine),
    scipy.stats.expon.ppf(0.999, scale=scale_nine),
    1000
)

axarr[2, 1].plot(x_nine, scipy.stats.expon.pdf(x_nine, scale=scale_nine), 'r-', lw=2)
axarr[2, 1].set_xlim(0, 5000)
axarr[2, 1].set_ylim(0, 0.001)
axarr[2, 1].set_title('b = 10, k = 9')
axarr[2, 1].hist(result_nine_times, normed=True)

rate_ten = compute_theoretical_rate(n, 10)
print("The rate for k = 10 is %.6f" % rate_ten)

scale_ten = 1 / rate_ten

x_ten = np.linspace(
    scipy.stats.expon.ppf(0.001, scale=scale_ten),
    scipy.stats.expon.ppf(0.999, scale=scale_ten),
    1000
)

axarr[2, 2].plot(x_ten, scipy.stats.expon.pdf(x_ten, scale=scale_ten), 'r-', lw=2)
axarr[2, 2].set_xlim(0, 50)
axarr[2, 2].set_ylim(0, 0.15)
axarr[2, 2].set_title('b = 10, k = 10')
axarr[2, 2].hist(result_ten_times, normed=True)

plt.show()
