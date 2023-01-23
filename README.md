# RasPass
A physical, encrypted password manager that has fingerprint authorization. After
user has been authorized, they can use retrieve desired password through a
companion GUI displayed on their computer.

## Laptop GUI Companion
Basic design idea for the companion GUI app:

Initial startup view:
![Inital Startup view](/App/imgs/Homepage.jpg "Initial Startup View")

After authentication via fingerprint, switch to password view:
![Password Manager view](/App/imgs/PasswordView.jpg "Password Manager view")

# Build Setup
First, you need to install the Pico SDK.

To build the project:
```
mkdir build
cd build
cmake ..
make
```
The resulting executable is in `main.uf2`. To load this onto the Pico, hold the BOOTSEL button on the board and connect it to your computer via USB. The board should mount as a drive. Copy the `main.uf2` file onto this drive, and the board should reboot (and the drive will be unmounted) as soon as it is loaded.


## Dependencies
Python 3.9+

Pico-W-Go extension for working with VSCode, or Thonny IDE

MicroPython installed on Pico

pySerial library: pip3 install pyserial


## Authors
Sara Deutscher, Hafsa Khan, Alex Mous, Audrey Yip, and Ludvig Liljenberg

## License
For open source projects, say how it is licensed.
