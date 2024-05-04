# Design PCB Action Recorder

Design PCB Action Recorder (DPAC) is a plugin specifically designed for KiCad that allows use to record their actions when designing PCB layout and export a `.csv` file of each step.

**Note:** This plugin has only been tested with KiCad 7.0. It's likely incompatible with later versions.

## Setup
Launch KiCad and navigate to the folder where plugins are stored.
    - Go to: `Kicad -> Tools -> External Plugins -> Open plugin Directory`

Open a terminal and change directory to the plugin folder:
```bash
cd [path-to-plugins-folder]
```

Clone the DAPE-plugin repository:
```bash
git clone https://github.com/fleaxiao/DP_plugin.git
```

Refresh your plugins in KiCad:
    - Go to: Kicad -> Tools -> External Plugins -> Refresh Plugins.

The DPAC plugin should now be visible within the menu of KiCad.

## Usage

1. ``Start Record:`` The components of a Buck conveter will be intialized with random positions, and these components will be overlapped. The size of PCB board is fixed to `100mm x 160mm`. 
2. ``End Record:`` After manual design (select, move and rotate of footprint), a `.csv` file containg a state squence of each footprint will be exported.
3. ``Abandon Record:`` The current design will be delected.