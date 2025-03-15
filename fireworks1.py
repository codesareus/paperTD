import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.colors import hsv_to_rgb

def create_firework(ax):
    """Create a single firework explosion"""
    x = np.random.uniform(-0.5, 0.5)
    y = np.random.uniform(0, 1)
    n_particles = 200
    angles = np.linspace(0, 2*np.pi, n_particles)
    radius = np.random.uniform(0.05, 0.5)
    
    # Create particles with different colors and trajectories
    for angle in angles:
        hue = np.random.uniform(0, 1)
        color = hsv_to_rgb([hue, 1, 1])
        
        # Particle trajectory
        t = np.linspace(0, 1, 50)
        x_traj = x + radius * t * np.cos(angle)
        y_traj = y + radius * t * np.sin(angle) - 0.5 * t**2  # Parabolic motion
        
        # Fade out effect
        alpha = 1 - t
        
        ax.plot(x_traj, y_traj, color=color, alpha=alpha[0], 
                marker='o', markersize=3, linestyle='')

def fireworks_animation():
    """Create and display fireworks animation"""
    start_time = time.time()
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Set up plot aesthetics
    ax.set_xlim(-1, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    
    placeholder = st.empty()
    
    while time.time() - start_time < 30:  # Run for 10 seconds
        ax.clear()
        ax.set_xlim(-1, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Create multiple fireworks
        for _ in range(np.random.randint(1, 6)):
            create_firework(ax)
        
        # Display in Streamlit
        placeholder.pyplot(fig)
        plt.pause(0.1)
        plt.clf()
    
    plt.close()

# Streamlit UI
st.title("🎆 Fireworks Show!")
st.write("Click the button below to start the 10-second fireworks display!")

if st.button("Launch Fireworks!"):
    fireworks_animation()
    st.write("Fireworks show complete! 🎇")
