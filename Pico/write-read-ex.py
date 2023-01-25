# Internal File System Use Example
# write multiple lines of text, each containing multiple data items to a file for reading into a spreadsheet

# Append ("a"): add more data (so inserting new username-password combinations)
# Write ("w"): edit/change data (so updating existing username-password combination)
# Read ("r"): read data 
# input() recieve user input 
# flush(): writes buffer to file so more data can be written without closing file 

#Open, Write, Close a datafile
data_file = open("MyData.txt","a")           # Creates/Opens a file called MyData.txt for writing
while True:
    print("Please enter username:")
    Username = input()
    data_file.write(Username + " ")
    data_file.flush() 
    print("Please password:")
    Password = input()
    data_file.write(Password + "\n")
    data_file.flush() 
    print("Done? (y/n):")  
    Done = input()
    if (Done == "y"):
        break
data_file.close()                            # Tidy up by closing file
print("Wrote data to file\n\n")

#Open, Read, Close a datafile
data_file = open("MyData.txt","r")   # Opens a file called MyData.txt for reading
Text_Data = data_file.read()         # Read data from the file into a variable
print(Text_Data)                     # print out the file data
data_file.close()                    # Tidy up by closing file
print("\n\n Done printing file data\n\n")