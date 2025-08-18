from tkinter import *
import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd
import numpy as np
import webbrowser

root = Tk()

root.title("Spectronaut to MiST Converter")

root.geometry('750x400')

#adding a label to the root window
lbl = Label(root, text = "Make sure your Spectronaut Output tsv file has the following columns:")
lb2 = Label(root, text = "'PG.ProteinAccessions', 'PG.MolecularWeight', 'PEP.MS1Quantity', 'R.FileName'")
lbl.grid()
lb2.grid()

#button = Button (root, text = "I understand", command = root.destroy())
button = Button(root, text = "I understand", command = root.destroy)

button.grid()

root.mainloop()

application_window = tk.Tk()
application_window.title("Loading...")
application_window.geometry('750x400')


#Ask the user to select a single file name.
answer = filedialog.askopenfilename(parent=application_window,
                                    initialdir=os.getcwd(),
                                    title="Please select a file:")

combined = pd.read_csv(answer, sep="\t")

print("combined")

#Format multi-protein cells
def split_specific_columns(df, columns_to_split, delimiter=";"):
    new_rows = []

    for _, row in df.iterrows():
        # Check if any of the target columns have a delimiter
        if all(delimiter not in str(row[col]) for col in columns_to_split):
            new_rows.append(row.to_dict())
            continue

        # Split target columns
        split_values = {col: str(row[col]).split(delimiter) for col in columns_to_split}
        
        # Validate: all columns must split to same length
        split_lengths = [len(vals) for vals in split_values.values()]
        if len(set(split_lengths)) != 1:
            raise ValueError(f"Split columns have mismatched lengths: {split_lengths}")

        # Duplicate the unchanged columns
        other_columns = [col for col in df.columns if col not in columns_to_split]
        for i in range(split_lengths[0]):
            new_row = {col: split_values[col][i].strip() for col in columns_to_split}
            for col in other_columns:
                new_row[col] = row[col]
            new_rows.append(new_row)

    return pd.DataFrame(new_rows)

combined = split_specific_columns(
    combined,
    columns_to_split=["PG.ProteinAccessions", "PG.MolecularWeight"]
)

#Convert PG.MolecularWeight  and PEP.MS1Quantity to numeric
combined["PG.MolecularWeight"] = pd.to_numeric(combined["PG.MolecularWeight"], errors="coerce")
combined["PEP.MS1Quantity"] = pd.to_numeric(combined["PEP.MS1Quantity"], errors="coerce")

#Simplify EXP ID names (optional)
combined["R.FileName"] = combined["R.FileName"].str.replace('21770_Cass_20240906_90_103_334156_', '')

# Estimate length as MolecularWeight // 110 (using floor division to round to the nearest integer to be compatible with MiST)
combined["Length"] = combined["PG.MolecularWeight"] // 110

#Convert NaN to 0s
combined["PEP.MS1Quantity"] = combined["PEP.MS1Quantity"].fillna(0)

# Define baits 
# In this case, there was only 1 bait
def extract_bait_name(filename):
    return "[INSERT BAIT]"

combined["Bait"] = combined["R.FileName"].apply(extract_bait_name)

# Aggregate per protein per source file
agg_df = combined.groupby(["PG.ProteinAccessions", "R.FileName"])["PEP.MS1Quantity"].mean().unstack(fill_value=0)
agg_df = agg_df.reset_index().rename(columns={"PG.ProteinAccessions": "Prey"})

# Calculate mean length per protein
#Note: All the proteins listed should be the same PG.MolecularWeight (and hence, Length), but I did this to prevent duplicate errors
length_df = combined.groupby("PG.ProteinAccessions")["Length"].mean().reset_index()

agg_df["Prey"] = agg_df["Prey"].astype(str).str.strip()
length_df["PG.ProteinAccessions"] = length_df["PG.ProteinAccessions"].astype(str).str.strip()


# Merge mean Length into agg_df (ensuring Length only appears once in the final tsv)
agg_df = agg_df.merge(length_df, left_on="Prey", right_on="PG.ProteinAccessions", how="left")
agg_df = agg_df.drop(columns=["PG.ProteinAccessions"])

# More formatting for MiST web input
agg_df["#"] = "#"
agg_df["BaitSims"] = "#"

# Re-order columns
cols = ["Prey", "#", "Length", "BaitSims"] + list(agg_df.columns.difference(["Prey", "#", "Length", "BaitSims"]))
agg_df = agg_df[cols]

# Create the custom multi-row header
header_1 = ["#", "#", "#", "Exps"] + list(agg_df.columns[4:])
header_2 = ["#", "#", "#", "Baits"] + ["[INSERT BAIT]"] * (len(agg_df.columns) - 4)
header_3 = ["Prey", "#", "Length", "BaitSims"] + ["[INSERT BAIT]"] * (len(agg_df.columns) - 4)

# Write the final table to a TSV file
with open("mistinput_GUI.tsv", "w") as f:
    f.write("\t".join(header_1) + "\n")
    f.write("\t".join(header_2) + "\n")
    f.write("\t".join(header_3) + "\n")
    agg_df.to_csv(f, sep="\t", index=False, header=False)


application_window.destroy()

print("Saved mistinput_GUI")

#Turn into a box
print("Now add your baits")

bait = Tk()

bait.title("Spectronaut to MiST Converter")

bait.geometry('750x400')

#adding a label to the root window
bait_lbl = Label(bait, text = "Conversion Complete!")
bait_lb2 = Label(bait, text = "Now, your MiST input tsv will be opened in Excel. Make sure to input your bait(s) in rows 2 and 3 Columns E to F")
bait_lbl.grid()
bait_lb2.grid()

#button = Button (root, text = "I understand", command = root.destroy())
bait_button = Button(bait, text = "I understand", command = bait.destroy)

bait_button.grid()

bait.mainloop()


#For windows
os.startfile("mistinput_GUI.tsv")

print("opened csv")
#Then a box with link to MiST 

mist = Tk()

mist.title("Spectronaut to MiST Converter")

mist.geometry('750x400')

#adding a label to the root window
mist_lbl = Label(mist, text = "MiST Input is ready!")
mist_lb2 = Label(mist, text = "Click below to be redirected to the MiST web tool")
mist_lbl.grid()
mist_lb2.grid()

#button = Button (root, text = "I understand", command = root.destroy())
mist_button = Button(mist, text = "MiST", command = webbrowser.open_new(r"https://modbase.compbio.ucsf.edu/mist/"))

mist_button.grid()

mist.mainloop()

print("Program Complete")
#Exit Program

