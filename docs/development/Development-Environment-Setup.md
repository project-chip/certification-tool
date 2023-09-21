<!--
 *
 * Copyright (c) 2023 Project CHIP Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
-->
# Develop CHIP Test Harness on Raspberry Pi

Default development environment for Matter is using [VSCode](https://code.visualstudio.com) and [Dev Containers](https://containers.dev).

Matter TH must run on Ubuntu 22.04, if your workstation does not run Ubuntu, you need a separate machine to run Matter TH (Ubuntu Virtual Machine, Raspberry Pi 4, etc).


## Prerequisites 
### Workstation Setup
- [VSCode](https://code.visualstudio.com) installed on your workstation
- VSCode extensions installed: 
    - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
    - [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
    - [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) 
- [Docker](https://www.docker.com/get-started/) installed on your workstation

### Matter TH Host Setup
First you must get Matter TH running on Ubuntu 22.04
- Git clone of Matter TH root project
- Install ubuntu or Raspberry pi script in `./scripts/`

## Development on Workstation different from Matter TH Host
When using a workstation diffent from the host running Matter TH we use a Docker context to connect to the running Docker containers on the Matter TH host. This will guide you thru that setup.

### Initial setup
You only need to do this once on your workstation.

#### Configure Docker Context For Matter TH Host
1. Determine Matter TH host ip address or hostname eg. `192.168.64.8`
2. Verify that you can successfully ssh to Matter TH host with username. 
    
    Example:
    ```sh
    ssh mikaelhm@192.168.64.8
    ```
3. Decide a context name, eg. `matter-context`
4. Add Docker context via cli: 

    ```sh
    docker context create <context-name> --docker "host=ssh://<ssh-username>@<ip-or-hostname>"
    ```
    
    Example:
    ```sh
    docker context create matter-context --docker "host=ssh://mikaelhm@192.168.64.8"
    ```
5. Select docker context using Docker cli: 

    ```sh
    docker context use <context name>
    ```
    
    Example:
    ```sh
    docker context use matter-context
    ```

## Starting Development environment

1. On Matter TH Host, start the TH in `frontend` or `backend` development mode.

    Example for backend
    ```sh
    ./scripts/start.sh --backend-dev
    ```

    Example for frontend
    ```sh
    ./scripts/start.sh --frontend-dev
    ```

    This will start the TH as normal, except for the container that will be used for development. Eg. for backend the python server will not be started when using `--backend-dev`, as the developer can then manually start the server in debug mode.

2. Launch VS Code on Workstartion
3. Connect to `backend` or `frontend` container on Matter TH Host, via Docker tab in VSCode.

    Under containers there should be a `backend:latest` and a `frontend:latest`, plus `postgres` and `traefik`.

    Left click and selecting `Attach Visual Studio Code` on the container you want to connect VSCode to.

    VS Code will open a new window attached inside the docker container with all dev-tools available.
4. First time connecting VSCode, you need to "Open Folder" `/app/backend` or `/app/frontend`.
5. Additionally, you might be propted to install recommended extensions. Please install them all.


NOTE: in-order to use git inside VS Code you must setup credential sharing:
(https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)[https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials]



## Troubleshooting

#### VSCode opens unexpected folder when attaching to container check the imageConfig on workstation:

    1. Open new VS Code window (No folder open and not attached to container)
    2. Open Control pallet (CMD+SHIFT+P or F1)
    3. Open "Remote-Containers: Open Container Configuration"
    4. Select image "backend:latest" or "frontend:latest"
    5. Verify `workspaceFolder` is set to the expected `/app/backend` or `/app/frontend`


### When running backend server, sqlalchemy does not find user

    ```
    ...
    sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "user" does not exist
    LINE 2: FROM "user" 
                ^

    [SQL: SELECT "user".id AS user_id, "user".full_name AS user_full_name, "user".email AS user_email, "user".hashed_password AS user_hashed_password, "user".is_active AS user_is_active, "user".is_superuser AS user_is_superuser 
    FROM "user" 
    WHERE "user".email = %(email_1)s 
    LIMIT %(param_1)s]
    [parameters: {'email_1': 'admin@admin.com', 'param_1': 1}]
    ```
    
    reset database by running `python backend/scripts/reset_db.py` in backend container

## Useful commands
- `docker context ls` : lists all the docker contexts. Can be used to verify if `chippi` context is created successfully
- `docker context rm <context-name>` : removes a docker context
- `docker context use <context-name>` : changes the docker context to `<context-name>`


## Reset DB
-   Run the `scripts/reset_db.py` script inside the backend container to drop and create a database, and run all the database migrations.