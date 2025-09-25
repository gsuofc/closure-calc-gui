# Closure Calc Gui
Calculate the closure for a survey plan using a series of line segments

![Closure Calc GUI Screenshot, with grid of inputs on the left and visual diagram on the right](https://github.com/gsuofc/closure-calc-gui/blob/main/screenshot.png?raw=true)

### Basic Usage
This program requires Python 3, turtle, and tkinter to be installed in order to function. Use the checkbox to select if a segment is a curve or a line, and enter the measurements of the segment. Segments have the following fields:
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
 
### Keyboard Controls:
Shift + Arrow Keys: Move selected text box
Space: Toggle Curve
Return: Go to next row, first column
Tab: Go to next column
Shift+Tab: Go to previous column

### Other Features
Save: Saves the current set of segments to file (JSON)
Load: Loads a set of segments from file (JSON)
Generate Report: Creates a report with information on the closure, and the list of segments (TXT)
Export as CSV: Creates a ENU formatted CSV file for use in CAD

### Licensing
This code is licensed under [public domain](https://github.com/gsuofc/closure-calc-gui?tab=CC0-1.0-1-ov-file). You are permitted to use this code for any reason, without restriction. 
