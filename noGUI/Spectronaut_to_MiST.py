import pandas as pd
import numpy as np


#Load your Spectronaut output report
combined = pd.read_csv("/Users/cardi/Box/MiST/Spectronautoutput_sample.tsv", sep="\t")

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
with open("mistinput_.tsv", "w") as f:
    f.write("\t".join(header_1) + "\n")
    f.write("\t".join(header_2) + "\n")
    f.write("\t".join(header_3) + "\n")
    agg_df.to_csv(f, sep="\t", index=False, header=False)
