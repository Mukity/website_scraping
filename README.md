# Description
Scraping data from different websites for different use cases. E.g. To extract vehicle data

# Initialization
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


# Usage
- Entry point of the application is the scrape.py file.
- Interacting with the application is via command-line
Example:
```
python scrape.py <mode> <region> --sub_mode <sub_mode> <optional parameters>
```
## Description of parameters
### Required
Modes available
1. vehicle
2. upload_dave

#### Vehicle
Regions available for vehicle include:
1. usa
2. mena

Sub-modes are dependent on the region selected.
* usa
    1. cars 
* mena
    1. yalla
    2. benz
    3. dubi
    4. automax

The 2 modes yalla and benz cover various areas within the mena region.
I.e.
- benz has the following places
    1. dubai
    1. abu-dhabi
    1. ksa
    1. qatar
    1. kuwait
    1. bahrain
    1. oman
    1. lebanon
    1. iraq
    1. jordan

- Yalla on the other hand has the following places
    1. ksa
    1. uae
    1. egypt
    1. qatar
    1. oman
    1. kuwait
    1. bahrain

Important Notes
1. Dubai and Abu-dhabi are both part of the UAE region.
2. ksa is Kingdom of Saudi Arabia
3. uae is United Arab Emirates which comprises of 7 states.

### Optional
The optional parameters are passed as part of the kwargs parameter
Example:
> python scrape.py vehicle mena --sub_mode yalla --kwargs '{"_cached": true}'

NOTE: The parameters passed in the kwargs argument should be a string that is json loadable.

#### Kwargs arguments
1. **_cached** - determines whether to fetch all the data from the redis cache or not.
- Takes bool values. true or false
- When value supplied is true, the application checks for availability of the data in redis-db

2. **upload**
- Takes bool value i.e. true or false
- when upload is set to true, the generated car features are compiled and uploaded to the API configured in the code.

3. **max_pages**
- Takes integer values
- Parameter for restricting the number of pages to restrict the number of vehicles for the mode.
- In sub_modes where the flow involves quering by feature(s) first, this parameter controls the number of pages within the queried pages.

    Example of sub_mode: **yalla**

- On the other hand, for pages where querying is not necessary prior to feature extraction, then the number of pages restricts the number of pages for the mode.

    Example of sub_mode: **dubi** and **automax**

```
Example 
```
> python scrape.py vehicle mena --sub_mode yalla --kwargs '{"_cached": false, "upload": true, "max_pages": 3}'

#### upload_dave
- This mode consolidates vehicle data based on region specified and uploads to the DaveAI backend.
Has several regions:
- all the places in benz and yalla
- usa
- all
> python scrape.py upload_dave all