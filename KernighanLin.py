#! Python 3.7

DEBUG = False


class Edge(object):
    """ Edge object. Essentially another name for a net. Connects two & only two vertices together. This class is only
            used to parse files (load_matrix()), and link Vertex objects to each other.

    """
    def __init__(self, left, right):
        self.left_id = left
        self.right_id = right

    @property
    def left(self):
        return self.left_id

    @left.setter
    def left(self, new_left):
        self.left_id = new_left

    @property
    def right(self):
        return self.right_id

    @right.setter
    def right(self, new_right):
        self.right_id = new_right


class Vertex(object):
    def __init__(self, input_id):
        # integer id value
        self.id_val = input_id
        # Array of other vertices this vertex is connected to
        self.connections = []
        # integer group value
        self.grouping = None

    @property
    def id(self):
        return self.id_val

    @property
    def edges(self):
        return self.connections

    @property
    def group(self):
        return self.grouping

    @group.setter
    def group(self, group):
        self.grouping = group

    def add_vertex(self, new_connection):
        """ Function append a vertex to the list of vertices the vertex is connected to

        Args:
            new_connection (Vertex): a vertex object

        Returns:
            None.
        """

        if new_connection not in self.connections:
            self.connections.append(new_connection)

    def dump_connections(self):
        """Function to dump the id values of the connections to the given vertex

        Returns:
            None.
        """
        for x in self.connections:
            print(x.id, end=',')

    def get_cost(self):
        """ Function that checks the groups that the current vertex is connected to, and adds 1 to the cost if not in
                the same group.

        Returns:
            int: A cost based on the connections between the current node and its other nodes from the netlist

        """
        cost = 0

        for vertex in self.connections:
            if vertex.group is not self.group:
                cost += 1
            else:
                cost -= 1

        return cost


def load_matrix(filename):
    """ Function to load in a csv file, and create arrays for the algorithm to process

    Args:
        filename (str): A file to read from

    Returns:
        Array: An array of vertex types, all of which are linked to each other according to the given netlist
    """

    with open(filename) as f:
        # Local array. Used to check uniqueness of vertex objects.
        vertex_ids = []
        # Local array. Used to create a 1 to 1 netlist list.
        current_edges = []
        # Total output. Edges are the actual connections, and vertices are the nodes.
        edges = []
        vertices = []

        # Row by row, read off nets from file
        for row in f:
            # Remove the word net from the beginning of each line, and split it from the rest of the connections
            #       here, the variable "left" is unused.

            left, right = row[4:].split(':')

            '''
                Here what we want to do is two things. Create a list of connections, and create a list of nodes (vertex)
                Directly below is the handling of nodes. We'll split apart the netlist, and create unique vertex types
                    and push them to the array labeled "vertices"
                In the loop immediately after, we'll deal with printing out connections from the given net.
            '''

            for x in right.lstrip('\t').split('\t'):
                # Write the current connections we're dealing with to an array, so we can link them after creating the
                #       vertices.
                current_edges.append(int(x))
                # Check if this node has already been created here. If not, create it. We'll deal with linking the node
                #   to other nodes later.
                if int(x) not in vertex_ids:
                    vertex_ids.append(int(x))
                    vertices.append(Vertex(int(x)))

            # Iterate through the net and connect all nodes together with the Edge() function
            for y in current_edges:
                for connection in range(current_edges.index(y) + 1, len(current_edges)):
                    # Add new connection to the edges array
                    edges.append(Edge(y, current_edges[connection]))

            current_edges.clear()

    # Local pointer variable used in the following for loop
    vertex_pointer = None
    '''
        The following loop runs through the given vertices, and looks for connections in the edges array.
    '''
    for vertex in vertices:
        # Iterate through vertex, then iterate through edges to link the objects together
        for edge in edges:
            if vertex.id is edge.left:
                # Add connection with the right value of the edge

                # Iterate through the list of vertices and find the vertex that matches the id of the right value
                for inner_vertex in vertices:
                    if edge.right is inner_vertex.id:
                        vertex_pointer = inner_vertex

                # Link the found edge to the current vertex, and reset the pointer
                vertex.add_vertex(vertex_pointer)
                vertex_pointer = None

            elif vertex.id is edge.right:
                # Add connection with the left value of the edge

                # Iterate through the list of vertices and find the vertex that matches the id of the left value
                for inner_vertex in vertices:
                    if edge.left is inner_vertex.id:
                        vertex_pointer = inner_vertex

                # Link the found edge to the current vertex, and reset the pointer
                vertex.add_vertex(vertex_pointer)
                vertex_pointer = None

    return vertices


class VertexSetFunctions(object):
    def __init__(self, vertex_array):
        self.vertices = vertex_array
        self.group_a = []
        self.group_b = []
        if DEBUG:
            print('Loaded vertices.\n')

    def random_split(self):
        """ Simple function that takes the current given vertices and splits them in half arbitrarily.

        Returns:

        """
        if DEBUG:
            print('Cut nodes in half.')

        array_size = len(self.vertices)
        for group_a in range(0, int(array_size/ 2)):
            self.vertices[group_a].group = 0
            self.group_a.append(self.vertices[group_a])
        for group_b in range(int(array_size / 2), array_size):
            self.vertices[group_b].group = 1
            self.group_b.append(self.vertices[group_b])

    @staticmethod
    def do_swap(vertex_a, vertex_b):
        """ Function that swaps the assigned group of two vertices. Does NOT change the arrays group_a & group_b

        Args:
            vertex_a (Vertex): A vertex object to be swapped
            vertex_b (Vertex): A vertex object to be swapped

        Returns:
            None.
        """
        if vertex_a.group == vertex_b.group:
            raise AttributeError('Cannot swap vertices of the same group!')
        temp_group = vertex_a.group
        vertex_a.group = vertex_b.group
        vertex_b.group = temp_group

    def set_arrays(self):
        """ Function to place vertices in correct array groups if their groups have been swapped.

        Returns:
            None.
        """
        self.group_a.clear()
        self.group_b.clear()
        for vert in self.vertices:
            if vert.group is 0:
                self.group_a.append(vert)
            elif vert.group is 1:
                self.group_b.append(vert)
            else:
                raise AttributeError('Invalid grouping assigned to a vertex.')

    def sort_group_a(self):
        """ Function that runs through group a and orders the elements based on cost.

        Returns:
            None.
        """
        self.group_a.sort(key=lambda x: x.get_cost(), reverse=True)

    def sort_group_b(self):
        """Function that runs through group b and orders the elements based on cost.

        Returns:
            None.

        """
        self.group_b.sort(key=lambda x: x.get_cost(), reverse=True)

    def overall_cost(self, group):
        """ Function to sum up the overall cost of a given group

        Args:
            group (int): Group to evaluate total cost of.

        Returns:
            int: Cost of the given group.

        """
        cost = 0

        if group is 0:
            for vert in self.group_a:
                cost += vert.get_cost()
        elif group is 1:
            for vert in self.group_b:
                cost += vert.get_cost()
        else:
            raise ValueError('No such group.')

        return cost


def kernighan_lin_sort(input_matrix, prev_verts):
    """ Function that follows the Kernighan-Lin sorting algorithm to sort between two groups based on the calculated
            "cost" of each node. Returns two sorted arrays of nodes.

    Args:
        input_matrix (VertexSetFunctions): A set of vertices to manipulate
        prev_verts (List): Previous Vertex objects that have already been swapped

    Returns:
        a tuple containing two matrices of Vertex objects sorted by the Kernighan-Lin algorithm

    """

    '''
        We'll go through each Vertex in group_a, and create an improvement list based on each vertex's connection with
            vertices in group_b. With the exception of any vertices provided in the args of the function
    '''
    improvement_matrix = []

    # In the above list, "improvement_matrix", we'll store the following data
    #   A tuple in the following format
    #   (   The vertex used to compute improvement  ,   The vertex the cost was compared to ,   The cost of the swap   )

    for vert_a in input_matrix.group_a:
        for vert_b in input_matrix.group_b:
            if vert_a in prev_verts or vert_b in prev_verts:
                continue
            improvement_matrix.append((vert_a, vert_b, vert_a.get_cost() + vert_b.get_cost()))

    '''
        Next, we'll iterate through the arrays, and find out which ones can be improved upon. We'll keep track of our
        most valuable swap in the max_cost variable, along with the value of their improvement
    '''
    max_cost_vert_pair = [None, None]
    max_cost = -999999999
    _temp_index = None

    for improvement_tuple in improvement_matrix:
        if improvement_tuple[2] > max_cost:
            max_cost = improvement_tuple[2]
            max_cost_vert_pair[0] = improvement_tuple[0]
            max_cost_vert_pair[1] = improvement_tuple[1]

    '''
        From the above code, we've successfully obtained our most valuable swap, so we'll go ahead and perform the swap
    '''
    input_matrix.do_swap(max_cost_vert_pair[0], max_cost_vert_pair[1])

    '''
        Now we'll resort the groups, since we just reassigned two vertices to the others' groups
    '''
    input_matrix.set_arrays()

    '''
        Here, we can repeat the process until our overall cost is no longer decreasing.
    '''

    return max_cost_vert_pair


class DebugMethods:
    @staticmethod
    def dump_connections(input_vertices):
        """ Print the nodes & their connections to console

        Args:
            input_vertices: an array of Vertex types

        Returns:
            None.
        """
        for vert in input_vertices:
            print(vert.id,'\t: ', end='')
            vert.dump_connections()
            print('\b\n', end='')

    @staticmethod
    def dump_ids(input_vertices):
        for vert in input_vertices:
            print(vert.id,',', end='')
        print('\b')

    @staticmethod
    def dump_groups(input_vertices):
        """ Print the nodes & their groups to console

        Args:
            input_vertices: an array of Vertex types

        Returns:
            None.
        """
        for vert in input_vertices:
            print(vert.id, '\t: ', end='')
            print(vert.group)

    @staticmethod
    def dump_costs(input_vertices):
        """ Print the vertices & their cost to console

        Args:
            input_vertices: An array of Vertex types

        Returns:
            None.
        """
        for vert in input_vertices:
            print(vert.id, '\t: ', end='')
            print(vert.get_cost())


def main():

    filename = 'venv/netlist.txt'

    input_vertices = load_matrix(filename)

    matrix = VertexSetFunctions(input_vertices)

    matrix.random_split()

    matrix.sort_group_a()

    matrix.sort_group_b()

    print('--------------Starting Values-----------------')
    print('-- Group A --')
    DebugMethods.dump_costs(matrix.group_a)
    print('Overall Cost {0}'.format(matrix.overall_cost(0)))
    print('-- Group B --')
    DebugMethods.dump_costs(matrix.group_b)
    print('Overall Cost {0}'.format(matrix.overall_cost(1)))
    print('--------------Starting Values-----------------')

    previous_verts = []
    best_groups = [None, None, matrix.overall_cost(0) + matrix.overall_cost(1)]

    for it in range(int(len(matrix.group_a) / 2)):
        DebugMethods.dump_ids(previous_verts)
        out = kernighan_lin_sort(matrix, previous_verts)
        previous_verts.append(out[0])
        previous_verts.append(out[1])

        matrix.sort_group_a()

        matrix.sort_group_b()

        if matrix.overall_cost(0) + matrix.overall_cost(1) < best_groups[2]:
            best_groups[0] = matrix.group_a
            best_groups[1] = matrix.group_b
            best_groups[2] = matrix.overall_cost(0) + matrix.overall_cost(1)

        print('-------------------------------')
        print('-- Group A --')
        DebugMethods.dump_costs(matrix.group_a)
        print('Overall Cost {0}'.format(matrix.overall_cost(0)))
        print('-- Group B --')
        DebugMethods.dump_costs(matrix.group_b)
        print('Overall Cost {0}'.format(matrix.overall_cost(1)))

    print('----------------Final Arrangement-----------------')
    print('-- Group A --')
    DebugMethods.dump_ids(best_groups[0])
    print('-- Group B --')
    DebugMethods.dump_ids(best_groups[1])
    print('-- Overall Cost = {0} --'.format(best_groups[2]))
    print('---------------------------------------------------')
    print('-- Group A --')
    DebugMethods.dump_costs(best_groups[0])
    print('-- Group B --')
    DebugMethods.dump_costs(best_groups[1])

    # secondrun = VertexSetFunctions(best_groups[0] + best_groups[1])
    # secondrun.random_split()
    # print('-- Group A --')
    # DebugMethods.dump_ids(secondrun.group_a)
    # print('-- Group B --')
    # DebugMethods.dump_ids(secondrun.group_b)


if __name__ == "__main__":
    main()