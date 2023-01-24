# RasPass
A physical, encrypted password manager that has fingerprint authorization. After
user has been authorized, they can use retrieve desired password through a
companion GUI displayed on their computer.

## Pico Development Setup
In VSCode, configure `Pico` folder as `Pico W Go` project, and upload the project.

## Laptop GUI Companion
Basic design idea for the companion GUI app:

Initial startup view:

![Inital Startup view](/App/imgs/Homepage.jpg "Initial Startup View")

After authentication via fingerprint, switch to password view:

![Password Manager view](/App/imgs/PasswordView.jpg "Password Manager view")

## Dependencies (for development)
Python 3.9+

Pico-W-Go extension for working with VSCode, or Thonny IDE

MicroPython installed on Pico

pySerial library: pip3 install pyserial


## Authors
Sara Deutscher, Hafsa Khan, Alex Mous, Audrey Yip, and Ludvig Liljenberg

## License
For open source projects, say how it is licensed.
