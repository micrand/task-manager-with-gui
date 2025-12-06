# Kivy Task Manager

**Note:** This application is developed for educational purposes at BYU-Idaho.

## Overview

Task Manager with GUI is a desktop application built with Python and Kivy for managing tasks efficiently. It provides a simple and intuitive interface to add, edit, delete, and categorize tasks, mark them as completed, and save them locally.

## Features

* Add, edit, and delete tasks
* Mark tasks as completed (strikethrough text for completed tasks)
* Categorize tasks
* Due dates for tasks
* Save and load tasks from a JSON file (`tasks.json`)
* RecycleView-based task list for efficient rendering
* Grey-themed background for a clean interface
* Popup confirmation on saving tasks

## Installation

1. Ensure Python is installed on your system.
2. Install Kivy using pip:

   ```bash
   pip install kivy
   ```

## Usage

1. Clone or download the repository.
2. Run the application:

   ```bash
   python kivy_task_manager.py
   ```
3. Use the buttons to add, edit, or delete tasks.
4. Check the box to mark tasks as completed.
5. Click "Save Now" to save tasks immediately (a confirmation popup will appear).

## Task Structure

Each task contains the following fields:

* **Title:** Name of the task
* **Category:** Optional category to organize tasks
* **Description:** Optional detailed description
* **Due date:** Optional due date (YYYY-MM-DD)
* **Completed:** Status of the task (True/False)

## File Structure

* `task_manager.py` - Main Python file containing the app code
* `tasks.json` - JSON file where tasks are stored (created automatically when saving tasks)

## Customization

* **Background Color:** The app has a grey background. Modify `Window.clearcolor` in `task_manager.py` to change the theme color.
* **Task Appearance:** Completed tasks are displayed with strikethrough text.

## License

This project is open-source and available under the MIT License.
