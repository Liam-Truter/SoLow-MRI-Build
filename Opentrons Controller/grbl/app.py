from robot import Robot
import tkinter as tk
from tkinter import scrolledtext
import threading
import time


class App:
    def __init__(self):
        self.xlim = (0, 375)
        self.ylim = (0, 250)
        self.zlim = (-150, 100)

        self.positions = []
        self.robot = Robot()  # Initialize the robot instance

        # Step sizes
        self.step_sizes = [0.1, 0.5, 1, 5, 10, 50]
        self.step_size_idx = 2
        self.step_size = self.step_sizes[self.step_size_idx]

        # GUI elements
        self.root = None
        self.log_text = None

    def start(self):
        self.root = tk.Tk()
        self.root.title("Opentrons Field Mapper GUI")

        # Variable for radio button
        self.step_var = tk.IntVar()
        self.step_var.set(self.step_size_idx)  # Default to starting step size

        # Key bindings
        self._setup_key_bindings()

        # Step size radio button list
        self._setup_step_size_controls()

        # Head movement controls
        self._setup_movement_controls()

        # Log display
        self._setup_log_display()

        # Position Save button
        self._setup_position_save()

        # Start log update thread
        threading.Thread(target=self._update_logs, daemon=True).start()

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

    def _setup_log_display(self):
        log_frame = tk.Frame(self.root)
        log_frame.pack(pady=10, fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=50, state="disabled", wrap="word")
        self.log_text.pack(pady=5, padx=5, fill="both", expand=True)

    def _setup_position_save(self):
        frame_ps = tk.Frame(self.root)
        frame_ps.pack(pady=10)
        tk.Button(frame_ps, text="Save Position", command=self.save_position).pack()

    def _update_logs(self):
        """Continuously fetch and display logs."""
        while True:
            log_entry = self.robot.get_next_log_entry()
            if log_entry:
                log_type, message = log_entry
                self.log_text.configure(state="normal")
                if log_type == "output":
                    self.log_text.insert("end", f"{message}\n", "output")
                else:
                    self.log_text.insert("end", f"{message}\n", "input")
                self.log_text.configure(state="disabled")
                self.log_text.yview("end")  # Auto-scroll to the latest entry
            time.sleep(0.1)
            
            # Configure tag colors
            self.log_text.tag_config("output", foreground="blue")
            self.log_text.tag_config("input", foreground="black")

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

    def move_constrained(self, **kwargs):
        if "x" in kwargs.keys():
            kwargs["x"] = max(min(kwargs["x"], self.xlim[1]), self.xlim[0])
        if "y" in kwargs.keys():
            kwargs["y"] = max(min(kwargs["y"], self.ylim[1]), self.ylim[0])
        if "z" in kwargs.keys():
            kwargs["z"] = max(min(kwargs["z"], self.zlim[1]), self.zlim[0])
        self.robot.move_head(**kwargs)

    def move_forward(self):
        self.move_constrained(y=self.robot.pos[1] + self.step_size)

    def move_backward(self):
        self.move_constrained(y=self.robot.pos[1] - self.step_size)

    def move_left(self):
        self.move_constrained(x=self.robot.pos[0] - self.step_size)

    def move_right(self):
        self.move_constrained(x=self.robot.pos[0] + self.step_size)

    def move_up(self):
        self.move_constrained(z=self.robot.pos[2] + self.step_size)

    def move_down(self):
        self.move_constrained(z=self.robot.pos[2] - self.step_size)

    def save_position(self):
        bot_pos = self.robot.pos.tolist()
        self.positions.append(bot_pos)
        print(f"Saved position: {bot_pos}")


def main():
    app = App()
    app.robot.connect("COM6")
    app.robot.home()
    app.start()


if __name__ == "__main__":
    main()
