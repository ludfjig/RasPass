#Internal File System Use - Example #3
#write multiple lines of text, each containing multiple data items to a file for reading into a spreadsheet

#Open, Write, Close a datafile
data_file = open("MD.txt","w")           # Creates/Opens a file called MyData.txt for writing
Num_Lines = 0                                # Counter for number of lines to create
while Num_Lines < 5:                         # Loop 5 times
    Num_Lines += 1                           # Increment line counter
    Line = str(Num_Lines)                    # Convert line number to string data
    Text = Line + ", text line of data, 34, 12, 4\n"     # Create a variable for to use for data writing to file containing multiple data items
                                             # Using commas will allows the spreadsheet to sort the data for further processing
    data_file.write(Text)                    # Write data to the file
    data_file.flush()                        # Writes buffer to file so more data can be written without closing file  
data_file.close()                            # Tidy up by closing file
print("Wrote data to file\n\n")

#Open, Read, Close a datafile
data_file = open("MD.txt","r")   # Opens a file called MyData.txt for reading
Text_Data = data_file.read()         # Read data from the file into a variable
print(Text_Data)                     # print out the file data
data_file.close()                    # Tidy up by closing file
print("\n\n Done printing file data\n\n")