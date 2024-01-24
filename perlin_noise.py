import random
import math 
import matplotlib as mpl

mpl.use('TkAgg')            
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
import numpy as np

class PermutationTable():
    def __init__(self):
        self.__size = 25
        self.__seed = 2023
        self.__P = []
    
    #create permutation table according to seed and shuffle pseudo-randomly
    def make_permutation_table(self):
        random.seed(self.__seed)
        self.__P = [x for x in range(self.__size)]*2
        random.shuffle(self.__P)

    def set_size(self, size):
        self.__size = size

    def set_seed(self, seed):
        self.__seed = seed

    def get_P(self):
        return self.__P
        
    def get_seed(self):
        return self.__seed

    def get_size(self):
        return self.__size
    

class PerlinNoise():
    def __init__(self, pTableObj):
        self.__finalValues = []
        self.__octaveNum = 2
        self.__gridWidth = 5
        self.__gridLength = 5
        self.__resolution = 100
        self.__ampStep = 1/2
        self.__freqStep = 2 
        self.__P = pTableObj.get_P()      

    #linearly interpolate between two vectors
    def lerp(self, a, b, weight):
        return a+(weight*(b-a))

    # use smoothing function between two vectors
    def smoothing_func(self,t):
        return ((6*t - 15)*t + 10)*t*t*t

    #generate noise for a pixel using just the permutation table and no further inputs
    def basic_noise(self, x, y):
        G = [(1,1), (1,-1), (-1,1), (-1,-1)]

        xMin = math.floor(x)
        xMax = xMin + 1
        yMin = math.floor(y)
        yMax = yMin + 1

        possibleCoords = [(xMin, yMin), (xMax, yMin), (xMin, yMax), (xMax, yMax)]
        dotProducts = []
         
        # find dot product for each integer coordinate surrounding pixel
        for coord in possibleCoords:
            constVector = G[(self.__P[self.__P[coord[0]%self.__gridLength]+coord[1]%self.__gridWidth])%4]
            dotProduct = ((x-coord[0])*constVector[0])+((y-coord[1])*constVector[1])
            dotProducts.append(dotProduct)
        
        productA = self.lerp(dotProducts[0], dotProducts[1], self.smoothing_func(x%1))
        productB = self.lerp(dotProducts[2], dotProducts[3], self.smoothing_func(x%1))
        productC = self.lerp(productA, productB, self.smoothing_func(y%1))

        return productC 

    #create noise with octaves for the entire grid
    def complete_noise(self):
        amp = 1
        freq = 1
        self.__finalValues = self.apply_to_each_pixel(amp, freq)

        for x in range(self.__octaveNum):
            amp *= self.__ampStep
            freq *= self.__freqStep
            self.__finalValues = np.add(self.apply_to_each_pixel(amp, freq), self.__finalValues)                    

        #scale value down to -1, 1 range of Perlin Noise incase it went over it while octaves were being made
        maxVal = np.amax(self.__finalValues)
        minVal = np.amin(self.__finalValues)
       
        self.__finalValues = (((np.array(self.__finalValues)-minVal)/(maxVal-minVal))*2)-1   

    #go through each pixel on grid and generate noise
    def apply_to_each_pixel(self, amplitude, frequency):    
        values = []
        for x in range(self.__gridLength*self.__resolution):
            row = []
            for y in range(self.__gridWidth*self.__resolution):
                pixelVal = amplitude*self.basic_noise((x/self.__resolution)*frequency, (y/self.__resolution)*frequency)
                row.append(pixelVal)
            values.append(row)
        return values
    
    def set_width_length(self, width, length):
        self.__gridLength = length
        self.__gridWidth = width

    def set_octave_num(self, octaveNum):
        self.__octaveNum = octaveNum
    
    def set_resolution(self, res):
        self.__resolution = res

    def set_ampStep(self, ampStep):
        self.__ampStep = ampStep 

    def set_freqStep(self, freqStep):
        self.__freqStep = freqStep

    def get_width_length(self):
        return (self.__gridWidth, self.__gridLength)

    def get_octave_num(self):
        return self.__octaveNum 

    def get_resolution(self):
        return self.__resolution
    
    def get_ampStep(self):
        return self.__ampStep 
    
    def get_freqStep(self):
        return self.__freqStep
    
    def get_final_values(self):
        return self.__finalValues

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.pTableObj = self.instance_pTable(5, 5, 2023)  
        self.pNoiseObj = self.instance_pNoise(0, 5, 5, 100, self.pTableObj, 1/2, 2)
        
        self.create_display()

    def check_for_error(self, val, checkForInt, lowerLim=None, upperLim=None):
        try:
            if checkForInt:
                val = int(val)
            
            val = float(val)

            if lowerLim != None and val < lowerLim:
                return "outOfBounds" 
            if upperLim != None and val > upperLim:
                return "outOfBounds"

            return True

        except ValueError:
            return "wrongType"

    def display_error_message(self, errorDict):
        outOfBounds = ""
        wrongType = ""

        for x in errorDict.keys():
            if errorDict[x] == "wrongType":
                wrongType += x + ", "
            elif errorDict[x] == "outOfBounds":
                outOfBounds += x + ", "
        
        text = "The noise could not be generated because "
        textWrongType = "\nVariables: {} \nare of the wrong type".format(wrongType)
        textOutOfBounds = "\nVariables: {} \nare too large or too small.".format(outOfBounds)
        
        if wrongType != "":
            text += textWrongType
        if outOfBounds != "":
            text += textOutOfBounds
        
        messg = tk.Toplevel(self)
        messg.title("Error")
        tk.Label(messg, text=text).pack()

    #create Permutation table object
    def instance_pTable(self, width, length, seed):
        pTableObj = PermutationTable()
        pTableObj.set_size(width*length)
        pTableObj.set_seed(seed)
        # create permuatation table
        pTableObj.make_permutation_table()
        return pTableObj

    #create the complete Perlin Noise 
    def instance_pNoise(self, octaveN, width, length, resolution, pTable, ampStep, freqStep):
        pNoiseObj = PerlinNoise(pTable)
        pNoiseObj.set_octave_num(octaveN)
        pNoiseObj.set_width_length(width, length)
        pNoiseObj.set_resolution(resolution)
        pNoiseObj.set_ampStep(ampStep)
        pNoiseObj.set_freqStep(freqStep)
        pNoiseObj.complete_noise()
        return pNoiseObj

    def display_graph(self, graph, canvas):
        graph.clear()

        z = (self.pNoiseObj.get_final_values())

        x, y = np.meshgrid(range(z.shape[1]), range(z.shape[0]))

        graph.plot_surface(x,y,z,cmap="viridis")
        canvas.draw()
    
    def create_display(self):
        def handle_input_values(graph, canvas): 
            seed = seedEntry.get()
            xVal = xEntry.get()
            yVal = yEntry.get()
            octaveNum = octaveEntry.get()
            resolution = resEntry.get()
            ampStep = ampStepEntry.get()
            freqStep = freqStepEntry.get()
            
            resultDict = {"Seed": seed, "GridsizeX": xVal, "GridsizeY": yVal,
             "OctaveNumber": octaveNum, "Resolution": resolution, "AmplitudeStep": ampStep,
             "FrequencyStep": freqStep }
            
            issuesDict = {} 
            for x in resultDict.keys():
                if x == "Seed":
                    issuesDict[x] = self.check_for_error(resultDict[x], False)
                if x == "GridsizeX":
                    issuesDict[x] = self.check_for_error(resultDict[x], True, 1, 15)
                if x == "GridsizeY":
                    issuesDict[x] = self.check_for_error(resultDict[x], True, 1, 15)
                if x == "OctaveNumber":
                    issuesDict[x] = self.check_for_error(resultDict[x], True, 0, 20)
                if x == "Resolution":
                    issuesDict[x] = self.check_for_error(resultDict[x], True, 2)
                if x == "AmplitudeStep":
                    issuesDict[x] = self.check_for_error(resultDict[x], False)
                if x == "FrequencyStep":
                    issuesDict[x] = self.check_for_error(resultDict[x], False)
            
            for x in issuesDict:
                if issuesDict[x] != True:
                    self.display_error_message(issuesDict)
                    return None

            seed = float(seed)
            xVal = int(xVal)
            yVal = int(yVal)
            octaveNum = int(octaveNum)
            resolution = int(resolution)
            ampStep = float(ampStep)
            freqStep = float(freqStep)

            # get previous perlin noise values to check if Permutation Table has to be regenerated or if user hasn't changed input
            oldSeed = self.pTableObj.get_seed()
            (oldXVal, oldYVal) = self.pNoiseObj.get_width_length()
            oldOctaveNum = self.pNoiseObj.get_octave_num()
            oldResolution = self.pNoiseObj.get_resolution()
            oldAmpStep = self.pNoiseObj.get_ampStep()  
            oldFreqStep = self.pNoiseObj.get_freqStep() 
            
            if seed != oldSeed or (xVal, yVal) != (oldXVal, oldYVal) or octaveNum != oldOctaveNum or resolution != oldResolution or freqStep != oldFreqStep or ampStep != oldAmpStep:
                if seed != oldSeed or (xVal, yVal) != (oldXVal, oldYVal):
                    self.pTableObj = self.instance_pTable(xVal, yVal, seed)
                self.pNoiseObj = self.instance_pNoise(octaveNum, xVal, yVal, resolution, self.pTableObj, ampStep, freqStep)
            
            self.display_graph(graph, canvas)

        self.title("Perlin Noise")

        #inputs
        seedLabel = tk.Label(self, text = "Enter seed:")
        seedEntry = tk.Entry(self)
        seedEntry.insert(0, self.pTableObj.get_seed())
        
        gridSizeLabel = tk.Label(self, text = "Set grid size:")
        xLabel = tk.Label(self, text =  "Width")
        yLabel = tk.Label(self, text =  "Length")
        xEntry = tk.Entry(self)
        yEntry = tk.Entry(self)
    
        xEntry.insert(0, self.pNoiseObj.get_width_length()[0])
        yEntry.insert(0, self.pNoiseObj.get_width_length()[1])

        resLabel = tk.Label(self, text = "Set resolution: ")
        resEntry = tk.Entry(self)
        resEntry.insert(0, self.pNoiseObj.get_resolution())

        octaveLabel = tk.Label(self, text =  "Set octave number:")
        octaveEntry = tk.Entry(self)
        octaveEntry.insert(0, self.pNoiseObj.get_octave_num())

        freqStepLabel = tk.Label(self, text="Set rate of change \nof frequency:")
        freqStepEntry = tk.Entry(self)
        freqStepEntry.insert(0, self.pNoiseObj.get_freqStep())
        ampStepLabel = tk.Label(self, text="Set rate of change \nof amplitude:")
        ampStepEntry = tk.Entry(self)
        ampStepEntry.insert(0, self.pNoiseObj.get_ampStep())

        #make matplotlib display
        fig = Figure(figsize=(5,5))
        graph = fig.add_subplot(projection="3d")

        graph.set_box_aspect((self.pNoiseObj.get_width_length()[0], self.pNoiseObj.get_width_length()[1], (self.pNoiseObj.get_width_length()[0] + self.pNoiseObj.get_width_length()[1])/2))

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, rowspan=20, column=0, padx=30, pady=30)


        self.display_graph(graph, canvas)
        
        submitButton = tk.Button(self, text="SUBMIT", command = lambda: handle_input_values(graph, canvas))

        # place GUI elements on screen
        seedLabel.grid(row=0, column=1, columnspan=4)
        seedEntry.grid(row=1, column=1, columnspan=4)
        gridSizeLabel.grid(row=2, column=1, columnspan=4)
        xLabel.grid(row=3, column=1) 
        xEntry.grid(row=3, column=2)
        yLabel.grid(row=3, column=3)
        yEntry.grid(row=3, column=4)
        resLabel.grid(row=4, column=1, columnspan=4)
        resEntry.grid(row=5, column=1, columnspan=4)
        octaveLabel.grid(row=6, column=1, columnspan=4)
        octaveEntry.grid(row=7, column=1, columnspan=4)
        freqStepLabel.grid(row=8, column=1, columnspan=4)
        freqStepEntry.grid(row=9, column=1, columnspan=4)
        ampStepLabel.grid(row=10, column=1, columnspan=4)
        ampStepEntry.grid(row=11, column=1, columnspan=4)
        submitButton.grid(row=20, column=0)
    
def  main():    
    app = GUI()
    app.mainloop()

if __name__ == "__main__":
    main()