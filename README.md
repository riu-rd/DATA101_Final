# DATA101 Final Application

This is the repository for the data visualization application made from Plotly Dash for the DATA101 Final Project

## Consolidated EDA Files

All files that are used to do Exploratory Data Analysis is stored in this [Google Drive Link](https://drive.google.com/drive/folders/16gl_XkzblRBFiXGtehRJmr24hS63GvAw?usp=sharing)

## How to Run the Application

### Prerequisites:

- Preferred if Python and Anaconda is installed in the system
- Can run `pip` and `conda` commands
- Can create a virtual environment to ensure no dependency errors (optional)

### Creating a Virtual Environment with Conda

- Open Command Line Interface `cmd`
- Create a conda environment by running:

```bash
  conda create --name <name of your choice> python=3.11.8
```

- Activate the environment if it is not yet activated. It should show "(name of your choice)" before the path in your CLI.

```bash
  conda activate <name of your choice>
```

### Installing Dependencies for the application

- In your CLI, go to the root directory of the repository. There should be a requirements.txt file there.
- Install dependencies by running the following commands: (Note that you should still be inside your virtual environment)
  ```bash
  conda install -c conda-forge gdal
  ```
  ```bash
  pip install -r requirements.txt
  ```
- If there are no errors, you should be able to run the app smoothly along with the EDA files.
- Remember to run everything inside your virtual environment.

### Running the Application

- go to the `/app` directory
- Run:

```bash
python index.py
```
