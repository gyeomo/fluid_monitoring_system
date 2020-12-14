# fluid_monitoring_system


It is intended to prevent accidents caused by excessive administration of sap.

The position of the clamp, a fluid regulator, can be sent to the server for monitoring, and locks have been installed so that patients cannot arbitrarily manipulate the position of the clamp.

Arduino measures the clamp position with the variable resistance of the slide and then transmits it to the server using Bluetooth. In addition, RFID modules allow doors to be opened and closed, allowing only designated users to open them.

The server is written in Python and receives data via Bluetooth. The data received falls into a function that converts to a time when the sap drops. The time remaining with maximum capacity and calculated time was calculated and visualized.
