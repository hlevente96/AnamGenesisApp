# AnamGenesis

Generate anamnesis from EHR data using AI

Szlogen: "egy jó anamnézis fél diagnózis" ([link](https://www.hazipatika.com/napi_egeszseg/az_orvos_is_ember/cikkek/a-betegseg-mogott-mindig-ott-az-ember-interju-a-mok-lekoszono-alelnokevel))

---

# Data

The "raw" SYNTHEA `.csv` files should be stored locally in the `raw_data` folder in the top level of the repository, but they should not be pushed to GitHub!

---

# Streamlit App: How to Run

This guide provides step-by-step instructions to set up and run the Streamlit application using Poetry.

### 1. Clone the Repository  
Clone this repository to your local machine:
```bash
git clone <repository-url>
cd <repository-folder>
```
### 2. Install Dependencies
Use Poetry to install all the required dependencies specified in pyproject.toml:
```bash
poetry install
```
### 3. Activate the Poetry Environment
Start the Poetry shell to activate the virtual environment:
```bash
poetry shell
```
### 4. Run the Streamlit App
Launch the Streamlit application from the steamlit_app folder by running:
```bash
cd app
streamlit run app.py
```
### 5. Access the App
After running the command, Streamlit will provide a local URL in the terminal (e.g., http://localhost:8501). Open the URL in your web browser to view the app.

---

# Poetry usage

## Dependency Management Commands

- **Add a dependency**:  
  ```bash
  poetry add package_name
  
- **Add a development dependency**:  
  ```bash
  poetry add --dev package_name

- **Remove a dependency**:  
  ```bash
  poetry remove package_name
  
- **Update dependencies**:  
  ```bash
  poetry update
  
## Environment Management

- **Install project dependencies**:  
  ```bash
  poetry install
  
- **Activate the environment:**:  
  ```bash
  poetry shell
  
- **Deactivate the environment**:  
  ```bash
  exit
  
## Running and Building

- **Run a script within the Poetry environment**:  
  ```bash
  poetry run python script.py
  
- **Run tests or external commands**:  
  ```bash
  poetry run pytest
