---
date:
  created: 2017-04-01
readtime: 15
pin: true
links:
  slug: aprs
---

# Program Maxtrac with DosBox

![Program Maxtrac with DosBox](../../img/aprs.png)

I found a used Maxtrac 300 radio on eBay that I wanted to repurpose into an APRS tracker and realized I needed to program the APRS frequency. Here is how you use DoxBox to program your radio.

<!-- more -->

### Things you need:

- Maxtrac Radio
- Windows computer (I'm using Windows 10 x64)
- Motorola FTDI programming cable from Valley Enterprises
- FTDI Driver (http://www.ftdichip.com/Drivers/VCP.htm)
- DosBox Software (https://www.dosbox.com/)
- GM300 Software (gm300v.5.zip)

Install the FTDI Driver for Windows
Install the DosBox software
Download the GM300 software and extract it to C:\GM300
Plug in your FTDI USB cable and check Device Manager to see what COM port it was assigned:

### Locate your DosBox config file for editing

``` powershell
{system drive}:\Users\{username}\AppData\Local\DOSBox\dosbox-{version}.conf
```

### Open your DosBox configuration file and set the following variables:

``` console
core=auto
cputype=auto
cycles=fixed 191
cycleup=10
cycledown=20

serial1=directserial realport COM1
serial2=dummy
serial3=disabled
serial4=disabled

[autoexec]
# Lines in this section will be run at startup.
# You can put your MOUNT lines here.

MOUNT c C:\GM300
c:
```

Now when you run DosBox all you need to do is launch the program with

```
GM300.EXE
```

Here's what the Main Menu looks like when loaded

First you need to pull the current code plug off the radio before you can make changes
