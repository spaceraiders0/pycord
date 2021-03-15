# pycord
pycord is a command-line Discord client written, and extendible in Python.

# More information
Currently, pycord is not fully functional. The most I have got done is a basic
window management system, however it *is* quite flexible. The base idea of pycord
is that it revolves around a client-server model. You can have a daemon running
in the background, and clients that "hook up" to it, and request information from
it.
</br>
</br>
More information in the documentation folder.

# TODO-List
For those of you who might stumble across this little project, and would like to help contribute, I suggest you start here.
If you need to get a general understanding of how pycord *actually works*, then I suggest you check out the documentation
folder provided in the root directory of the project. However, there are some things that I need to complete.

✔️  = Completed
✖️  = Incomplete

Allow for windows to be inserted into columns at runtime ✖️
Setup a method of detecting keyboard input. ✖️
Load up information from the pycord daemon, and cache it in the client. ✖️
Implement "modes" similar to Vim. ✖️
Add a command mode. When launched, it should shift all windows up by 2 lines. ✖️
Implement a method of resizing windows. Ditching the "columns" might be necessary. ✖️
