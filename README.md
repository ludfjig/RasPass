# RasPass
A physical, encrypted password manager that has fingerprint authorization. After
user has been authorized, they can use retrieve desired password through a
companion App displayed on their computer.

## RasPass Design and Demo
### Click on Start Screen Image to be directed to video demo of the RasPass's functionality.
Initial startup view:

[![Inital Startup view](/App/imgs/StartScreen.png "Initial Startup View")](https://www.youtube.com/watch?v=Q_DuC9U03qs)

After authentication via master password, switches to password view:

![Password Manager view](/App/imgs/PasswordView.png "Password Manager view")

The user is able to get information about their login information for a certain website after authenticating with their fingerprint, prompted with the popup below:

![Successful fingerprint scan](/App/imgs/Success.png "Successful fingerprint scan")

If the scan is unsuccessful, it will show the number of attempts (caps at five):

![Unsuccessful fingerprint scan](/App/imgs/Failure.png "Unsuccessful fingerprint scan")

Which then shows the login information (which can be shown, hidden, and copied to clipboard):

![Login info view](/App/imgs/GetInfo.png "Login info view")

The user can also change their login information, which also needs fingerprint authentication. The popup for that is here:

![Change info view](/App/imgs/Update.png "Change info view")

Finally, there is a settings page where the user can see how many password entries they have left (for storage) and register/remove fingerprints for authentication.

![Settings view](/App/imgs/SettingsPopUp.png "Settings view")

## Pico Development Setup
Flash the Pico with the latest [Microython UF2](https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2) from Raspberry Pi (We tested on version 1.9.1-859)
> To do this the `bootsel` button must be held down when connecting the Pico to the computer.

In VSCode, open the `Pico` folder in a new VSCode window and connect the Pico device onto VSCode.

Configure the `Pico` folder project as `Pico W Go` project and upload the project.

> Another option is to use the [Thonny](https://thonny.org/) IDE for MicroPython to upload to the Pico. As it can be slightly more reliable than the `Pico W Go` Extension.

Afterwards, disconnect the Pico from VSCode and/or Thonny.

## Running the App
Make sure the Pico is disconnected from VSCode and/or Thonny.

Open a terminal and `cd` into `App`

Run the command `python3 RasPassApp.py` to start the desktop companion app!

## Dependencies (for development)
[Python 3.10+](https://www.python.org/downloads/)

[Pico-W-Go](https://github.com/paulober/Pico-W-Go) extension for working with VSCode
> Or [Thonny](https://thonny.org/) IDE

[Microython](https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2)  installed on Pico

[pySerial](https://pypi.org/project/pyserial/) library: pip3 install pyserial

[cryptography 39.0.1+](https://pypi.org/project/cryptography/) library: pip3 install cryptography

[pyperclip 1.8.2](https://pypi.org/project/pyperclip/) library: pip3 install pyperclip

[pillow 9.4.0](https://pypi.org/project/Pillow/) library: pip3 install pillow

[sv_ttk](https://pypi.org/project/sv-ttk/) library: pip3 install sv-ttk

## Known Bugs/Issues for further Development
* Formating of the `confirm` and `cancel` buttons for deleting a fingerprint
* Does not have a scroll bar for if the number of password entries exceeds the view window
* Master password not stored across powerloss due to issue with the fingerprint sensor itself
* No check on the strength of the passwords entered by the user

## Authors
Sara Deutscher, Hafsa Khan, Alex Mous, Audrey Yip, and Ludvig Liljenberg
