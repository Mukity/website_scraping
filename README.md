# Description
Scraping data from different websites for different use cases. E.g. To extract vehicle data

## Setting up the repository
1. Git clone this repository
> git clone git@github.com:Mukity/website_scraping.git

2. Initialize the required submodules
> git submodule update --init <path_to_submodule>

Example:
>git submodule update --init git@github.com:Mukity/vehicle_scraping.git

Available submodules are:
- vehicle_scraping

### setting up the virtual environment
1. Create virtual environment using python's venv module 

> python3 -m venv .env

2. Activate the virtual environment

> source .env/bin/activate

3. Install the webtools_library

> pip install webtools_library-0.0.1-py3-none-any.whl

4. Install the requirements from the requirements.txt file

> pip install -r requirements.txt

# Diagrams


# Structure
The application takes a modular structure with different applications integrated as submodules.
