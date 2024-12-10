from robot import robot
import tkinter as tk
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting

import utilities

class App:
    def __init__(self):
        self.positions = []
        self.valid_points = None

        # Default bore parameters
        self.bore_depth = 440
        self.bore_radius = 145
        self.spacing = 10

        # Step sizes
        self.step_sizes = [0.1, 0.5, 1, 5, 10, 50]
        self.step_size_idx = 2
        self.step_size = self.step_sizes[self.step_size_idx]

        # GUI elements
        self.root = None

    def start(self):
        self.root = tk.Tk()
        self.root.title("Opentrons Field Mapper GUI")

        # Variable for radio button
        self.step_var = tk.IntVar()
        self.step_var.set(self.step_size_idx)

        # Setup GUI components
        self._setup_key_bindings()
        self._setup_step_size_controls()
        self._setup_movement_controls()
        self._setup_position_save()
        self._setup_bore_settings()
        self._setup_generate_points()
        self._setup_visualize_points_button()

        self.root.mainloop()

    def _setup_key_bindings(self):
        self.root.bind('<Shift_L>', lambda event: self.increase_step())
        self.root.bind('<Control_L>', lambda event: self.decrease_step())
        self.root.bind('<w>', lambda event: self.move_forward())
        self.root.bind('<s>', lambda event: self.move_backward())
        self.root.bind('<a>', lambda event: self.move_left())
        self.root.bind('<d>', lambda event: self.move_right())
        self.root.bind('<e>', lambda event: self.move_up())
        self.root.bind('<q>', lambda event: self.move_down())

    def _setup_step_size_controls(self):
        step_selection = tk.Frame(self.root)
        step_selection.pack(pady=10)

        for i in range(len(self.step_sizes)):
            step_label = tk.Label(step_selection, text=str(self.step_sizes[i]))
            step_label.grid(row=0, column=i, padx=5)

            step_radio = tk.Radiobutton(
                step_selection,
                variable=self.step_var,
                value=i,
                command=self.step_size_selected,
            )
            step_radio.grid(row=1, column=i, padx=5)

    def _setup_movement_controls(self):
        frame_fblr = tk.Frame(self.root)
        frame_fblr.pack(pady=10)

        btn_width, btn_height = 5, 2

        tk.Button(frame_fblr, text="↑", command=self.move_forward, width=btn_width, height=btn_height).grid(row=0, column=1)
        tk.Button(frame_fblr, text="←", command=self.move_left, width=btn_width, height=btn_height).grid(row=1, column=0)
        tk.Button(frame_fblr, text="↓", command=self.move_backward, width=btn_width, height=btn_height).grid(row=1, column=1)
        tk.Button(frame_fblr, text="→", command=self.move_right, width=btn_width, height=btn_height).grid(row=1, column=2)

        frame_ud = tk.Frame(self.root)
        frame_ud.pack(pady=10)
        tk.Button(frame_ud, text="↑", command=self.move_up, width=btn_width, height=btn_height).grid(row=0, column=0)
        tk.Button(frame_ud, text="↓", command=self.move_down, width=btn_width, height=btn_height).grid(row=1, column=0)

    def _setup_position_save(self):
        frame_ps = tk.Frame(self.root)
        frame_ps.pack(pady=10)
        tk.Button(frame_ps, text="Add Position", command=self.add_position).grid(row=0, column=0,padx=5)
        tk.Button(frame_ps, text="Save Positions", command=self.save_positions).grid(row=0, column=1,padx=5)

    def _setup_bore_settings(self):
        frame_settings = tk.Frame(self.root)
        frame_settings.pack(pady=10)

        # Bore depth
        tk.Label(frame_settings, text="Bore Depth").grid(row=0, column=0)
        self.bore_depth_entry = tk.Entry(frame_settings)
        self.bore_depth_entry.insert(0, str(self.bore_depth))
        self.bore_depth_entry.grid(row=0, column=1)

        # Bore radius
        tk.Label(frame_settings, text="Bore Radius").grid(row=1, column=0)
        self.bore_radius_entry = tk.Entry(frame_settings)
        self.bore_radius_entry.insert(0, str(self.bore_radius))
        self.bore_radius_entry.grid(row=1, column=1)

        # Spacing
        tk.Label(frame_settings, text="Spacing").grid(row=2, column=0)
        self.spacing_entry = tk.Entry(frame_settings)
        self.spacing_entry.insert(0, str(self.spacing))
        self.spacing_entry.grid(row=2, column=1)

    def _setup_generate_points(self):
        frame_generate = tk.Frame(self.root)
        frame_generate.pack(pady=10)
        tk.Button(frame_generate, text="Generate Points", command=self.generate_points).pack()

    def _setup_visualize_points_button(self):
        frame_vis = tk.Frame(self.root)
        frame_vis.pack(pady=10)
        tk.Button(frame_vis, text="Visualize Points", command=self.visualize_points).pack()

    def increase_step(self):
        self.step_size_idx = min(len(self.step_sizes) - 1, self.step_size_idx + 1)
        self.step_size = self.step_sizes[self.step_size_idx]
        self.step_var.set(self.step_size_idx)

    def decrease_step(self):
        self.step_size_idx = max(0, self.step_size_idx - 1)
        self.step_size = self.step_sizes[self.step_size_idx]
        self.step_var.set(self.step_size_idx)

    def step_size_selected(self):
        self.step_size_idx = self.step_var.get()
        self.step_size = self.step_sizes[self.step_size_idx]

    def move_forward(self):
        pos = [0,self.step_size,0]
        utilities.move_relative(pos)

    def move_backward(self):
        pos = [0,-self.step_size,0]
        utilities.move_relative(pos)

    def move_left(self):
        pos = [-self.step_size,0,0]
        utilities.move_relative(pos)

    def move_right(self):
        pos = [self.step_size,0,0]
        utilities.move_relative(pos)

    def move_up(self):
        pos = [0,0,self.step_size]
        utilities.move_relative(pos)

    def move_down(self):
        pos = [0,0,-self.step_size]
        utilities.move_relative(pos)

    def add_position(self):
        bot_pos = utilities.get_position()
        self.positions.append(bot_pos)
        print(f"Saved position: {bot_pos}")

    def save_positions(self):
        # Save calibration points to a CSV file
        utilities.save_points("calibration_points.csv", self.positions)

    def generate_points(self):
        # Fit a cylinder to the saved positions
        points = np.array(self.positions)
        fitted_params = utilities.fit_cylinder(points)

        # Generate valid points
        x_origin = np.mean(points[:, 0]) + self.bore_depth/2
        y_origin = fitted_params[0]
        z_origin = fitted_params[1]
        radius = fitted_params[2]

        self.valid_points = utilities.get_valid_points_cartesian(
            x=x_origin,
            y=y_origin,
            z=z_origin,
            r=radius,
            l=self.bore_depth,
            spacing=self.spacing
        )

        # Save valid points to CSV
        utilities.save_points("valid_points.csv", self.valid_points)
        print("Valid points saved to valid_points.csv")
    
    def visualize_points(self):
        if self.valid_points is None or len(self.valid_points) == 0:
            print("No valid points to visualize!")
            return

        # Create a Matplotlib 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        # Unpack points
        x, y, z = self.valid_points[:, 0], self.valid_points[:, 1], self.valid_points[:, 2]
        
        # Plot the points
        ax.scatter(x, y, z, c='blue', marker='o', s=10)

        # Set axis labels
        ax.set_xlabel('X [mm]')
        ax.set_ylabel('Y [mm]')
        ax.set_zlabel('Z [mm]')
        
        ax.set_title('Valid Points Visualization')
        plt.show()


def main():
    app = App()
    utilities.connect_robot()
    app.start()


if __name__ == "__main__":
    main()
