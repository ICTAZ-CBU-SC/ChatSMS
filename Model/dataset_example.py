class Dataset:
    class DatasetEntry:
        def __init__(self):
            pass

    def __init__(self):
        self._data = []


features = ['conversations', 'source', 'score', 'text']

"""
dataset[5]["conversations"] = [
    {'content': 'How do astronomers determine the original wavelength of light emitted by a celestial body at rest, 
    which is necessary for measuring its speed using the Doppler effect?',
    'role': 'user'},
    
    {'content': 'Astronomers make use of the unique spectral fingerprints of elements found in stars. These elements 
    emit and absorb light at specific, known wavelengths, forming an absorption spectrum. By analyzing the light 
    received from distant stars and comparing it to the laboratory-measured spectra of these elements, astronomers 
    can identify the shifts in these wavelengths due to the Doppler effect. The observed shift tells them the extent 
    to which the light has been redshifted or blueshifted, thereby allowing them to calculate the speed of the star 
    along the line of sight relative to Earth.',
    'role': 'assistant'}
]

---------------------------------------------------------------------------------------

dataset[5]["source"] = "WebInstructSub_axolotl"

---------------------------------------------------------------------------------------

dataset[5]["score"] = 5.025244235992432

---------------------------------------------------------------------------------------

dataset[5]["text"] = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: 26 July 2024

<|eot_id|><|start_header_id|>user<|end_header_id|>

How do astronomers determine the original wavelength of light emitted by a celestial body at rest, which is necessary for measuring its speed using the Doppler effect?<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Astronomers make use of the unique spectral fingerprints of elements found in stars. These elements emit and absorb light at specific, known wavelengths, forming an absorption spectrum. By analyzing the light received from distant stars and comparing it to the laboratory-measured spectra of these elements, astronomers can identify the shifts in these wavelengths due to the Doppler effect. The observed shift tells them the extent to which the light has been redshifted or blueshifted, thereby allowing them to calculate the speed of the star along the line of sight relative to Earth.<|eot_id|>"

"""
