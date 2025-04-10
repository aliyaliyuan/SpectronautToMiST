#splitcsv

#change directory of terminal to where split_tsv.py is
#When running this in the terminal you need to run the following line:

#python split_tsv.py '/path/to/large/csv' '/output/directory' 200000
#The number is the number of lines you are splitting it per tsv file

import os
import argparse

def split_tsv(input_file, output_dir, lines_per_file):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        header = infile.readline()
        file_count = 1
        output_file = os.path.join(output_dir, f'split_{file_count}.tsv')
        outfile = open(output_file, 'w', encoding='utf-8')
        outfile.write(header)
        
        line_count = 0
        for line in infile:
            if line_count >= lines_per_file:
                outfile.close()
                file_count += 1
                output_file = os.path.join(output_dir, f'split_{file_count}.tsv')
                outfile = open(output_file, 'w', encoding='utf-8')
                outfile.write(header)
                line_count = 0
            
            outfile.write(line)
            line_count += 1
        
        outfile.close()
    print(f'Successfully split {input_file} into {file_count} smaller files.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a large TSV file into smaller chunks.")
    parser.add_argument("input_file", help="Path to the large TSV file")
    parser.add_argument("output_dir", help="Directory to save the split files")
    parser.add_argument("lines_per_file", type=int, help="Number of lines per split file")
    
    args = parser.parse_args()
    split_tsv(args.input_file, args.output_dir, args.lines_per_file)
