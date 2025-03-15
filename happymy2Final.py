import time
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tempfile
import os

# Set up the Streamlit app title
st.title("Fireworks Animation")

# Define the shapes of letters and numbers with improved coordinates
def get_letter_shapes():
    # Coordinates for the characters (scaled and centered)
    H = np.array([
        [-0.8, -1], [-0.8, 1],  # Left vertical
        [0.8, -1], [0.8, 1],    # Right vertical
        [-0.8, 0], [0.8, 0]     # Horizontal bar
    ]) * 1.5
    
    Two = np.array([[-1, 1], [0, 1], [-1, 0], [-1, -1], [0, -1]]) * 2

    # Points for "Y"
    Y = np.array([[-1, 1], [0, 0], [0, -1], [0.25, 0], [1, 1]]) * 2

    # Edges for each character (explicit connections between points)
    letter_edges = {
        'H': [(0, 1), (2, 3), (4, 5)],  # Connect left, right, and middle bars
        'A': [(0, 1), (1, 2), (2, 3), (4, 5)],  # Triangle and horizontal bar
        'P': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],  # Circular P
        'Y': [(0, 1), (1, 2), (2, 3), (2, 4)],  # Correct "Y" shape
        'M': [(0, 1), (1, 2), (2, 3), (3, 4)],  # Peaks of M
        '2': [(0, 1), (1, 2), (2, 3), (2, 4)]  # Curved 2
    }

    return {
        'H': H, 
        'A': np.array([[-1, -1], [-0.5, 1], [0.5, 1], [1, -1], [-0.5, 0], [0.5, 0]]) * 2,
        'P': np.array([[-1, -1], [-1, 1], [0, 1], [1, 0], [-1, 0]]) * 2,
        'Y': Y,  # Updated "Y" points
        'M': np.array([[-1, -1], [-1, 1], [0, 0], [1, 1], [1, -1]]) * 2,
        '2': Two
    }, letter_edges

# Modified firework generation with better particle control
def generate_firework(ax, x_center, y_center, is_word=False, character=None):
    letter_shapes, letter_edges = get_letter_shapes()
    if is_word and character:
        num_particles_per_point = 15  # Increased particle density
        letter_shape = letter_shapes[character]
        edges = letter_edges[character]
        x, y = [], []
        
        # Add intermediate points for better shape definition
        for edge in edges:
            start_idx, end_idx = edge
            start = letter_shape[start_idx]
            end = letter_shape[end_idx]
            points = np.linspace(start, end, 5)
            for point in points:
                offsets = np.random.normal(loc=point, scale=0.1, size=(num_particles_per_point, 2))
                x.extend(offsets[:, 0] + x_center)
                y.extend(offsets[:, 1] + y_center)
        
        scatter = ax.scatter(x, y, s=20, c=np.random.rand(3,), alpha=0.95, edgecolors="none")
    else:
        num_particles = 200
        num_center_particles = int(num_particles * 0.2)
        num_outer_particles = num_particles - num_center_particles
        center_x = np.random.normal(loc=x_center, scale=0.5, size=num_center_particles)
        center_y = np.random.normal(loc=y_center, scale=0.5, size=num_center_particles)
        angles = np.linspace(0, 2 * np.pi, num_outer_particles)
        radii = np.random.uniform(1, 4, size=num_outer_particles)
        outer_x = x_center + radii * np.cos(angles)
        outer_y = y_center + radii * np.sin(angles)
        x = np.concatenate([center_x, outer_x])
        y = np.concatenate([center_y, outer_y])
        scatter = ax.scatter(x, y, s=15, c=np.random.rand(3,), alpha=0.9, edgecolors="none")
    return scatter

# Function to update the fireworks animation
def update(frame, ascending_fireworks, exploded_scatters, ax, series_launched):
    # Launch the series "HAPPY M Y 2" at frame 50
    if frame == 50 and not series_launched[0]:
        # In the update function's series launch section (around line 63):
        series_letters = ['H','A','P','P','Y', 'M','Y','2']  # Added None for space
        num_letters = len(series_letters)
        series_x = np.linspace(-16, 16, num_letters)  # Wider spread
        explosion_heights = np.linspace(20, 27, num_letters)
        speed = 1.0
        for i in range(num_letters):
            char = series_letters[i]
            x_start = series_x[i]
            scatter = ax.scatter(x_start, -5, s=10, c="white", alpha=0.8)
            ascending_fireworks.append({
                "scatter": scatter,
                "x": x_start,
                "y": -5,
                "speed": speed,
                "explosion_height": explosion_heights[i],
                "character": char
            })
        series_launched[0] = True

    # Update ascending fireworks
    if ascending_fireworks:
        for firework in ascending_fireworks.copy():
            firework["y"] += firework["speed"]
            firework["scatter"].set_offsets([firework["x"], firework["y"]])
            if firework["y"] >= firework["explosion_height"]:
                if "character" in firework:
                    exploded_scatters.append(generate_firework(ax, firework["x"], firework["y"], is_word=True, character=firework["character"]))
                else:
                    if np.random.rand() < 0.3:
                        exploded_scatters.append(generate_firework(ax, firework["x"], firework["y"], is_word=True))
                    else:
                        exploded_scatters.append(generate_firework(ax, firework["x"], firework["y"]))
                firework["scatter"].remove()
                ascending_fireworks.remove(firework)

    # Update exploded fireworks particles
    if exploded_scatters:
        for scatter in exploded_scatters.copy():
            offsets = scatter.get_offsets()
            offsets[:, 1] -= 0.2
            scatter.set_offsets(offsets)
            current_alpha = scatter.get_alpha()
            new_alpha = max(0.0, min(1.0, current_alpha - 0.02))
            scatter.set_alpha(new_alpha)
            if new_alpha <= 0:
                scatter.remove()
                exploded_scatters.remove(scatter)

    # Add new ascending fireworks occasionally
    if frame % 10 == 0:
        x_start = np.random.uniform(-10, 10)
        y_start = -5
        explosion_height = np.random.uniform(15, 40)
        speed = np.random.uniform(0.5, 1.0)
        scatter = ax.scatter(x_start, y_start, s=10, c="white", alpha=0.8)
        ascending_fireworks.append({
            "scatter": scatter,
            "x": x_start,
            "y": y_start,
            "speed": speed,
            "explosion_height": explosion_height
        })

def main():
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_xlim(-30, 30)
    ax.set_ylim(-10, 40)
    ax.axis("off")

    ascending_fireworks = []
    exploded_scatters = []
    series_launched = [False]  # Track if series has been launched

    ani = FuncAnimation(fig, update, frames=200, fargs=(ascending_fireworks, exploded_scatters, ax, series_launched), interval=50, blit=False)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmpfile:
        try:
            ani.save(tmpfile.name, writer="pillow", fps=20)
            gif_path = tmpfile.name
        except Exception as e:
            st.error(f"Failed to save animation: {e}")
            return

    if st.button("Play Fireworks"):
        st.write("Playing fireworks...")
        st.image(gif_path, use_container_width=True)
        time.sleep(40)

    if os.path.exists(gif_path):
        os.unlink(gif_path)

if __name__ == "__main__":
    main()
