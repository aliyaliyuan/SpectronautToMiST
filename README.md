# SpectronautToMiST
This converts large Spectronaut .tsv reports to a .tsv file that is compatible with MiST (https://modbase.compbio.ucsf.edu/mist/) for protein protein interaction analysis. The Spectronaut .tsv report needs to have the following columns: R.FileName,PG.MolecularWeight,PG.ProteinAccession,PEP.MS1Quantity. 

# Dependencies
pandas, numpy, glob

# Workflow

![raw files put into Spectronaut for analysis](https://github.com/user-attachments/assets/d79520ed-dcdf-430c-839f-67e005ef38b9)

# Data Visualization

Once you have the MiST results, remove the header so that the first row is simply the column names: "Bait" "Prey"	"Reproducibility"	"Abundance"	"Specificity"	"MiST". Then, use the Upset-Plot.rmd to generate an upset plot to see the overlap of identified preys from your baits. The preys that are present in all baits are likely nonspecific. Look into the ones only specific to your experimental. 

