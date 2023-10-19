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

# CSA Certification Tool

## About

With the goal of simplifying development, testing, and certification of devices, the Connectivity Standards Alliance has developed a standardized set of tools as well a test harness that is presently used for Matter certifications.

To learn more about the open-source [Matter SDK](https://github.com/project-chip/connectedhomeip), please read more [here](https://github.com/project-chip/connectedhomeip)

## Project Overview

### Goals

The test tooling, harness, and scripts are developed with the following goals and principles in mind:

**Proven:** The test harness and tools are built with and on top of existing technologies where possible.

**Robust:** The test harness and tools should be reliable and dependable.

**Low Cost:** The test harness and tools should run on low cost and accessible devices.

**Flexible:** The test harness and tools are flexible enough to accommodate deployment in different environments.

**Easy to Use:** The test harness and tools provide a smooth, cohesive, integrated experience.

**Open:** The Project’s design and technical processes are open and transparent
to the general public, including non-members wherever possible.

# Instructions

Detailed instructions for how to use this set of tools with [Matter](https://github.com/project-chip/connectedhomeip) are located [here](./docs/Matter_User_Guide/Matter_User_Guide.md)

## Related Repositories

Please be aware of these related repositories that all have to be used in concert to build, develop with, and use the certification tools

-   [Tool Frontend](https://github.com/project-chip/certification-tool-frontend)
-   [Tool Backend](https://github.com/project-chip/certification-tool-backend)
-   [CLI Tool ](https://github.com/project-chip/certification-tool-cli)
-   [Matter Test Scripts](https://github.com/project-chip/matter-test-scripts)

## Minimum Hardware Requirements

-   SD card 64 GB or mo
-   RaspberryPi 4 or newer with at least 4 GB RAM

## License

The test harness and tools are released under the [Apache 2.0 license](./LICENSE).
