# Building a custom MSI installer for Windows

You can white label the LimaCharlie installer for Windows by using an MSI wrapper.  By going through this process you can not only brand the installer to show your name / details, but you can also make installation of the Sensor easier for end users.  We have provided instructions below on how to use a 3rd party tool called [exemsi](https://www.exemsi.com/).

## Prerequisites

1. An MSI wrapper application, such as the exemsi application referenced in the instructions below
2. A digital code signing certificate  (optional, but highly recommended)

Without a digital code signing certificate the installer will show a warning that it is from an unknown publisher.

## Instructions

1. Download the [LimaCharlie sensor EXE](https://downloads.limacharlie.io/sensor/windows/64)
2. Download the [MSI Wrapper application from exemsi.com](https://exemsi.com)
3. Install the exemsi application on your computer
4. Launch the exemsi application and go through the EXE to MSI Converter Wizard steps as shown below:

5. Select the executable

* Set the `Setup executable input file name` to be the LimaCharlie EXE that you'd downloaded
* Optionally, specify a MSI output file name of your choosing (e.g. Acme_Installer.msi)
* Set the MSI platform architecture to match the executable (i.e. x86 for 32-bit, and x64 for 64-bit)

6. Set the visibility in Apps & features

7. Set the Security and User Context

8. Specify Application IDs

* In the Upgrade Code section, click the "Create New" button next to generate a code.  This will be used to allow uninstallation.

9. Specify Properties (optional: customize options here to have the installer show your brand)

* You can change the drop-down menu of each line item from "Executable" to "Manual" in order to set your own values for the Product Name, Manufacturer, Version, Comments, and Product icon

10. Specify More Properties (optional)

11. Specify Parameters

    * In the "Install arguments" box, enter "-i", add a space and then enter your [installation key](https://doc.limacharlie.io/docs/documentation/docs/manage_keys.md)
    * -i YOUR_INSTALLATION_KEY_GOES_HERE

To provide the option to uninstall, set the Uninstall argument to "-c" (note that you do not need to specify your Installation Key for uninstallation).

12. Actions

13. Summary

14. Status

Once you have created the MSI package you should sign it using your digital signature.  You can [learn more about signing the MSI on the exemsi website](https://www.exemsi.com/documentation/sign-your-msi/).

## Experience when running the MSI

When installing the application using the MSI you'll see your application name in the title bar.

When inspecting the properties of the MSI you'll see the details you'd specified.

In the Apps & Features section of Windows, you'll see the application listed under your name.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.
