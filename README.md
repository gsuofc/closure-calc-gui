# ![Closure Calc GUI Icon, showing a depiction of a survey plan with a large closure](https://raw.githubusercontent.com/gsuofc/closure-calc-gui/refs/heads/main/icon.png)  Closure Calc Gui 
Calculate the closure for a survey plan using a series of line segments
### Download
Download the lastest stable build from the [releases](https://github.com/gsuofc/closure-calc-gui/releases) page, or the latest committed build from [the actions tab](https://github.com/gsuofc/closure-calc-gui/actions) (subject to github actions data retention - note that older builds will be removed by github).

![Closure Calc GUI Screenshot, with grid of inputs on the left and visual diagram on the right](https://raw.githubusercontent.com/gsuofc/closure-calc-gui/refs/heads/main/screenshot.png)

### Basic Usage
This program requires Python 3, turtle, and tkinter to be installed in order to function (PyGithub is required for update checking). When ran as an .exe, all required python libraries are bundled in. 

Use the checkbox to select if a segment is a curve or a line, and enter the measurements of the segment. Segments have the following fields:
- Line:
  - Bearing (Deg,Min,Sec)
  - Distance
- Curve:
  - Delta (Deg,Min,Sec)
  - Arc Length
  - Radius
  - Radial Bearing (Optional)
 
##### Field Properties:
Specific functionality will occur when fields are formatted as follows:
- Line Bearing left blank: Re-uses final bearing from previous segment
- Distance with negative value: Adds 180 degrees to the bearing
- Delta left blank: Computes curve using Arc Length, rather than delta
- Radius left blank: Re-uses radius from previous segment
- Radius with negative value: Curves clockwise rather than counter-clockwise
- Radial Bearing left blank: Re-uses final bearing from previous segment
- Math Evaluation: In distance, Arc Length, Degrees, and Radius fields enter math statements to be evaluated (i.e. `5.5*8+1`)
 
### Keyboard Controls:
Shift + Arrow Keys: Move selected text box

Space: Toggle Curve

Return: Go to next row, first column

Tab: Go to next column

Shift+Tab: Go to previous column

F5: Recalculate the closure

### Plan View Controls:
Left click + drag: Pans the plan view

Scroll wheel: Zooms the plan view in and out

### Other Features
Save: Saves the current set of segments to file (JSON)

Load: Loads a set of segments from file (JSON)

Clear: Clears all segments without saving to start fresh

Generate Report: Creates a report with information on the closure, and the list of segments (TXT)

Export as CSV: Creates a ENU formatted CSV file for use in CAD

### Settings
Enable Math Eval: Toggle the ability to enable Math Evaluation. Disabling this feature will break any closures that used this feature

Enable Update Prompt at Startup: Check for updates at startup, and prompt if there is an update

Automatically Compute Closure: Compute the closure after editing a field. With this disabled, editing can be done by using the "Compute Closure" button in the menu or by using F5


### Building and Running
`closure-calc.py` can be run using `python closure-calc.py`. Alternatively, this program can be built using PyInstaller by performing the following

```
python gen_version_number.py
python -m PyInstaller --onefile -w closure-calc.py
```

A .bat file `build.bat` has been included to automate this process

### Licensing
This code is licensed under [public domain](https://github.com/gsuofc/closure-calc-gui?tab=CC0-1.0-1-ov-file). You are permitted to use this code for any reason, without restriction. 
