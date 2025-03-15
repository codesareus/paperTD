import time
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tempfile
import os

# Set up the Streamlit app title
st.title("Fireworks Animation")

# Function to generate fireworks particles after explosion
def generate_firework(ax, x_center, y_center):
    num_particles = 200  # Total number of particles
    num_center_particles = int(num_particles * 0.2)  # 20% of particles at the center
    num_outer_particles = num_particles - num_center_particles  # Remaining particles spread outward

    # Generate particles at the center
    center_x = np.random.normal(loc=x_center, scale=0.5, size=num_center_particles)
    center_y = np.random.normal(loc=y_center, scale=0.5, size=num_center_particles)

    # Generate particles spreading outward
    angles = np.linspace(0, 2 * np.pi, num_outer_particles)
    radii = np.random.uniform(1, 4, size=num_outer_particles)  # Random radii for outward particles
    outer_x = x_center + radii * np.cos(angles)
    outer_y = y_center + radii * np.sin(angles)

    # Combine center and outer particles
    x = np.concatenate([center_x, outer_x])
    y = np.concatenate([center_y, outer_y])

    # Scatter plot for the firework particles
    scatter = ax.scatter(
        x, y, s=15, c=np.random.rand(3,), alpha=0.9, edgecolors="none"
    )  # Larger particle size
    return scatter

# Function to update the fireworks animation
def update(frame, ascending_fireworks, exploded_scatters, ax):
    # Update ascending fireworks
    for firework in ascending_fireworks:
        firework["y"] += firework["speed"]  # Move firework upward
        firework["scatter"].set_offsets([firework["x"], firework["y"]])

        # Check if the firework has reached its explosion height
        if firework["y"] >= firework["explosion_height"]:
            exploded_scatters.append(generate_firework(ax, firework["x"], firework["y"]))
            firework["scatter"].remove()  # Remove the ascending firework marker
            ascending_fireworks.remove(firework)

    # Update exploded fireworks (particles)
    for scatter in exploded_scatters:
        offsets = scatter.get_offsets()
        offsets[:, 1] -= 0.2  # Particles move downward slowly
        scatter.set_offsets(offsets)
        scatter.set_alpha(max(0.1, scatter.get_alpha() - 0.02))  # Fade out particles

    # Add new ascending fireworks occasionally
    if frame % 10 == 0:  # Add a new firework every 20 frames
        x_start = np.random.uniform(-10, 10)  # Random x position
        y_start = -5  # Start below the visible area
        explosion_height = np.random.uniform(15, 42)  # Random explosion height
        speed = np.random.uniform(0.5, 1.0)  # Speed of ascent

        # Create a marker for the ascending firework
        scatter = ax.scatter(x_start, y_start, s=10, c="white", alpha=0.8)
        ascending_fireworks.append({
            "scatter": scatter,
            "x": x_start,
            "y": y_start,
            "speed": speed,
            "explosion_height": explosion_height
        })

# Main function to run the animation
def main():
    # Create a Matplotlib figure with a dark background
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("black")  # Set the figure background to black
    ax.set_facecolor("black")  # Set the axes background to black
    ax.set_xlim(-30, 30)  # Expanded x-axis limits to accommodate larger fireworks
    ax.set_ylim(-10, 40)  # Expanded y-axis limits to accommodate higher explosions
    ax.axis("off")

    # Initialize lists for tracking fireworks
    ascending_fireworks = []  # Fireworks that are still ascending
    exploded_scatters = []  # Fireworks that have exploded

    # Create the animation
    ani = FuncAnimation(fig, update, frames=200, fargs=(ascending_fireworks, exploded_scatters, ax), interval=50, blit=False)

    # Save the animation as a temporary GIF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmpfile:
        ani.save(tmpfile.name, writer="pillow", fps=10)
        gif_path = tmpfile.name

    # Display the "Play" button
    if st.button("Play Fireworks"):
        st.write("Playing fireworks for 10 seconds...")
        st.image(gif_path, use_container_width=True)  # Display the GIF in Streamlit
        time.sleep(10)  # Keep the GIF displayed for 10 seconds

    # Clean up the temporary GIF file
    if os.path.exists(gif_path):
        os.unlink(gif_path)

# Run the app
if __name__ == "__main__":
    main()
