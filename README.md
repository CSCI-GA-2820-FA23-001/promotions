# NYU DevOps Project: Promotion

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-FA23-001/promotions/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-001/promotions/actions)
[![Build Status](https://github.com/CSCI-GA-2820-FA23-001/promotions/actions/workflows/bdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-001/promotions/actions)

This repository contains code for Customer promotions for an e-commerce web site. 

## Overview


This repository contains the project undertaken by the Promotion Squad for CSCI-GA.2820-001 DevOps and Agile Methodologies. The project established the promotional functionalities of an e-commerce website, empowering customers to take advantage of various promotions for discounts. It provides all the essential operations, enabling users to create, read, update, delete, and list promotions by using the RESTful API. Each promotion is detailed with information such as id, name, description, start date, and more, all stored within a PostgreSQL database model.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Run

Make sure to set any required environment variables before running the app. Run the Flask App locally by typing the following command:
```
flask run
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes

k8s/                - Kubernetes yaml
├── deployment.yaml 
├── ingress.yaml
├── postgres.yaml
├── pv.yaml
└── serice.yaml

.tekton/            - tekton yaml
├── pipeline.yaml   - CI/CD pipelines
├── tasks.yaml      - tasks in pipelines
└── workspace.yaml  - PVC for pipelines
└── events          - event listener and trigger
    ├── event_listener.yaml 
    ├── route.yaml          
    └── trigger_binding.yaml
    └── trigger_template.yaml

features/           
├── environment.py          - Behave testing environment
├── promotions.features     - Promotion service back-end
└── steps              
    ├── promotion_steps.py  - Steps file for promotions.feature
    └── web_step.py         - Steps file for web interactions with Selenium
```

## Database model:
Promotion:
| Field | Type | Constraints |
|-------|--------|------------|
| id | Integer | primary key |
| name | String(63) | not nullable |
| description | String(63) | - |
| products_type | String(63) | not nullable |
| promotion_code | String(63) | - |
| require_code | Boolean | not nullable, default: False |
| start_date | Date | not nullable, default: today's date |
| end_date | Date | not nullable, default: today's date |



## Available Commands
```
create_promotions  POST     /promotions                   
delete_promotions  DELETE   /promotions/<int:promotion_id>
index              GET      /                             
list_promotions    GET      /promotions                   
read_promotions    GET      /promotions/<int:promotion_id>
update_promotions  PUT      /promotions/<int:promotion_id>
static             GET      /static/<path:filename>
```


## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
