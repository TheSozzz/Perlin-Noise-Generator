# Perlin-Noise-Generator
Program that generates perlin noise using matplotlib's interactive graph display. 
## Usage:
Press "Submit" after editing any of the input fields to regenerate the noise. 
Interact with the graph by using the left mouse button to rotate and right mouse button to zoom. 

The input options are:
- **seed**
  This sets the integer seed for the random function that will generate the Permutation Table used for the constant vector values in the noise.
- **width, length**
  This sets the size of the grid, so how many constant vectors and you want generated (width x length in total)
- **octave number**
  This sets the amount of octaves the noise will have, or how many times noise (modified by the amplitude and frequence rates) will be added on top of noise to create a more complex heightmap.
- **rate of change of frequency**
  This sets by how much each octave will be scaled horizontally 
- **rate of change of amplitude**
  This sets by how much each octave will be scaled vertically 


