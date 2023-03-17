# RasPass
A physical, encrypted password manager that has fingerprint authorization. After
user has been authorized, they can use retrieve desired password through a
companion GUI displayed on their computer.

## Pico Development Setup
Flash the Pico with the latest Microython UF2 from Raspberry Pi (![download link](https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2). We tested on version 1.9.1-859)


In VSCode, open the `Pico` folder in a new VSCode window and connect the Pico device onto VSCode.

Configure the `Pico` folder project as `Pico W Go` project and upload the project.

Afterwards, disconnect the Pico from VSCode.

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

## Running the App
Make sure the Pico is disconnected from VSCode and/or Thonny.

Open a terminal and `cd` into `App`

Run the command `python3 RasPassApp.py` to run the desktop companion app!

## Dependencies (for development)
Python 3.10+

Pico-W-Go extension for working with VSCode, or Thonny IDE

MicroPython installed on Pico

pySerial library: pip3 install pyserial


## Authors
Sara Deutscher, Hafsa Khan, Alex Mous, Audrey Yip, and Ludvig Liljenberg
