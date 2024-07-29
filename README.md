# Ludlum_Monitoring
DEVELOPMENT OF RADIATION  MONITORING SYSTEM USING WEBSITE-BASED IOT USING RASPBERRY AND LUDLUM 375

![Schematic_Brin_PkL_Project_2024-07-05 (2)](https://github.com/user-attachments/assets/ec9a6bb0-c860-4b62-8474-6150c138ba1e)

The project will work when the device is turned on, the Ludlum sensor will start reading the surrounding radiation level. If the sensor is not read, the website will display the message “Sensor Not Read”. If the sensor is read, the radiation data will be sent to the database and displayed on the website. Data from the sensor will be sent to the Raspberry Pi. If the data is not sent, the sending process will be repeated until successful. If the Raspberry Pi successfully reads the data, the LED will light up according to the following logic if the radiation level (n) is less than 10 µSv / hour, the green LED will light up, the radiation level (n) is more than 8.5 µSv / hour, the yellow LED will light up and buzzer and if the radiation level (n) is more than 10 µSv / hour, the red LED will light up and buzzer. In facing the challenges behind this case study, it is necessary to discuss the important materials and approaches used to design and solve the solution of the problems contained in the case study.


