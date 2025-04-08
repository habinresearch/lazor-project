from blocks import ReflectBlock, OpaqueBlock, RefractBlock
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def find_lazor_endpoint(lazor_grid, x, y, vx, vy, grid_size_x, grid_size_y):
    """
    Trace a lazor's path until it exits the grid or interacts with a block.

    Args:
        lazor_grid (Board): The current board configuration.
        x, y (int): Starting coordinates of the lazor.
        vx, vy (int): Lazor direction vector.
        grid_size_x (int): Width of the lazor grid.
        grid_size_y (int): Height of the lazor grid.

    Returns:
        tuple: (end_x, end_y, [list of new direction vectors])
    """
    is_first_turn = True
    new_directions = []  # Default: no new directions

    while (0 < x < grid_size_x and 0 < y < grid_size_y) or is_first_turn:
        x += vx
        y += vy
        found_collision = False

        blocks = lazor_grid.get_placed_blocks()
        for block in blocks:
            if block.within_boundaries(x, y):
                # Get new beam directions from block's interaction.
                new_directions = block.interact((vx, vy), (x, y))
                if new_directions:
                    # Ensure we have a list of direction vectors.
                    if isinstance(new_directions[0], (list, tuple)):
                        new_directions = [list(direction)
                                          for direction in new_directions]
                    else:
                        new_directions = [list(new_directions)]
                found_collision = True
                break  # Stop at the first collision

        if found_collision:
            # Only return new directions if still within bounds
            if 0 <= x <= grid_size_x and 0 <= y <= grid_size_y:
                return x, y, new_directions
            else:
                # Beam already out-of-bound; do not propagate further.
                return x, y, []

        if is_first_turn:
            is_first_turn = False

    # If while loop ended (i.e., beam went out-of-bound with no collision),
    # return no new directions.
    return x, y, []


def save_laser_image(lazor_grid, solution=None, filename=None):
    """
    Save a visualization of the Lazor grid, showing blocks, lasers, and target points.

    Args:
        lazor_grid (Board): Board instance with grid, lasers, and blocks.
        solution (list): Optional list of tuples (position, block_type_name) representing placed blocks.
        filename (str): Output file path for saving the image.
    """
    grid = lazor_grid.orig_grid
    x_size_grid = len(grid) * 2
    y_size_grid = len(grid[0]) * 2

    fig, ax = plt.subplots()
    ax.set_xlim(-1, y_size_grid + 1)
    ax.set_ylim(-1, x_size_grid + 1)

    # Add black border around the grid
    ax.add_patch(Rectangle((-1, -1), 1, x_size_grid + 3, color='black'))
    ax.add_patch(Rectangle((y_size_grid, -1), 1,
                 x_size_grid + 3, color='black'))
    ax.add_patch(Rectangle((-1, -1), y_size_grid + 3, 1, color='black'))
    ax.add_patch(Rectangle((-1, x_size_grid),
                 y_size_grid + 3, 1, color='black'))

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Map block class name to display character
    block_type_dict = {'ReflectBlock': 'A',
                       'OpaqueBlock': 'B', 'RefractBlock': 'C'}

    # Apply solution to grid
    if solution is not None:
        for (x, y), block_type in solution:
            grid[x][y] = block_type_dict.get(block_type, '?')

    # Draw the grid
    square_size = 2
    for x, row in enumerate(grid):
        for y, col in enumerate(row):
            if col == 'o':
                continue

            x_pos = x * 2 + 1
            y_pos = y * 2 + 1

            color = {
                'x': 'black',
                'A': 'green',
                'B': 'grey',
                'C': 'red'
            }.get(col, 'white')  # Default to white if unknown

            square = plt.Rectangle(
                (y_pos - square_size / 2, x_pos - square_size / 2),
                square_size, square_size, color=color
            )
            ax.add_patch(square)

    # Draw grid lines
    for i in range(0, x_size_grid + 1, 2):
        ax.plot([0, y_size_grid], [i, i], color='black', linewidth=1)
    for i in range(0, y_size_grid + 1, 2):
        ax.plot([i, i], [0, x_size_grid], color='black', linewidth=1)

    # Draw target points
    for px, py in lazor_grid.points:
        circle = plt.Circle((px, py), 0.2, color='black')
        ax.add_patch(circle)

    # Trace lazor beams
    lazors = lazor_grid.lasers.copy()
    while lazors:
        start_x, start_y, vx, vy = lazors.pop()

        end_x, end_y, new_dirs = find_lazor_endpoint(
            lazor_grid, start_x, start_y, vx, vy, x_size_grid, y_size_grid
        )

        # Draw the beam segment from start to end.
        lazor_length_x = end_x - start_x
        lazor_length_y = end_y - start_y

        ax.arrow(
            start_x, start_y,
            lazor_length_x, lazor_length_y,
            head_width=0.2, head_length=0.2, fc='red', ec='red'
        )

        # Only queue new beams if the endpoint is within bounds.
        if 0 <= end_x <= x_size_grid and 0 <= end_y <= y_size_grid:
            if new_dirs:
                for direction in new_dirs:
                    print(
                        f'Queuing new beam: {[end_x, end_y, direction[0], direction[1]]}')
                    lazors.append([end_x, end_y, direction[0], direction[1]])

    ax.axis("off")
    ax.set_aspect("equal")
    plt.gca().invert_yaxis()
    plt.savefig(filename, bbox_inches="tight")
    plt.close()
