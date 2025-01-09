# ![icon](images/icon.ico) PCB Design Action Recorder 

PCB Design Action Recorder (PDAR) is a plugin specifically designed for KiCad that allows user to record their actions when designing PCB layout and export a `.json` file of each step.

PDAR and PCB Design Action Labeler ([PDAL](https://github.com/fleaxiao/PDAL_plugin.git)) are series plugins. These plugins are recommend to use together, which fully log the human's thinking during PCB design process. Please make sure the constant.py files in each plugin are identical.

 > **Note:**  This plugin has only been tested with KiCad 8.0. It's likely incompatible with later versions.

## Setup

1. Launch `KiCad Command Prompt` and install the requirement of package in requirement.yml. 

2. Launch `KiCad` and download plugin.
    - Navigate to the folder where plugins are stored: `KiCad -> Tools -> External Plugins -> Open plugin Directory`

    - Open a terminal and change directory to the plugin folder:
        ```bash
        cd [path-to-plugins-folder]
        ```

    - Clone the PDAR_plugin repository:
        ```bash
        git clone https://github.com/fleaxiao/PDAR_plugin.git
        ```

    - Refresh your plugins in KiCad: `KiCad -> Tools -> External Plugins -> Refresh Plugins`

The PDAR plugin should now be visible in the menu of KiCad.

## Usage

1. Open both schematic file and PCB layout file. Make sure the PCB layout is empty. The footprints, tracks and vias are recommended to choose in the selection filter.

2. `Initialization:`  The components from the schematic will be imported to the PCB layout design environment. 

3. `Power Module & Sensitive Module:` Type the references of the modules which are high-current and signal-sensitive. The references should be separated by spaces.

4. `Start Record:` The components of a power converter will be initialized with random positions. The size of PCB board is configured in `constant.py`.

5. `End Record:` After manual design (select, move and rotate footprints; create tracks; place vias), a `.json` file containing a operation sequence of footprints, tracks, and vias will be exported.

6. `Abandon Record:` The current design will be deleted.

7. The suggested grid is **0.01 in**, and the via is recommended to place before wiring to make sure that the track is connected to the center of via.

## Acknowledge

The logo of this plugin is designed by bukeicon from Flaticon.

## Contact

If you have any questions, please contact me at x.yang2@tue.nl