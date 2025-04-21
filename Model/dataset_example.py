from datasets import load_dataset

"""
CSV Format
---------------------------------------------------------------------------
   id  |   Question                        |  Answer
---------------------------------------------------------------------------
   1   |                                    |   
   2   |                                    |   
   3   |                                    |   
---------------------------------------------------------------------------

"""


csv_file_path = "dataset.csv"
dataset = load_dataset("csv", data_files=csv_file_path, delimiter=",")


def convert_format(dataset_entry: dict):
    formatted_text = f"<human>: {dataset_entry['Question']}\n<bot>: {dataset_entry['Answer']}\n"
    return {"text": formatted_text}


# Apply function to convert dataset
dataset.map(convert_format)


# Remove other columns and keep only "text"
# Perform this operation on each split separately
for split in dataset.keys():
    columns_to_remove = [col for col in dataset[split].column_names if col != "text"]
    dataset[split] = dataset[split].map(lambda entry: {"text": entry["text"]},
                                        remove_columns=columns_to_remove)


# Function to extract human text
def extract_human_text(full_text: str):
    start_index = full_text.find("<human>:") + len("<human>:")
    end_index = full_text.find("<bot>:")
    return full_text[start_index:end_index].strip()


# Function to extract bot text
def extract_bot_text(full_text: str):
    start_index = full_text.find("<bot>:") + len("<bot>:")
    return full_text[start_index:].strip()


print(dataset["train"][5])
print(extract_human_text(dataset["train"][5]["text"]))
print(extract_bot_text(dataset["train"][5]["text"]))






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
