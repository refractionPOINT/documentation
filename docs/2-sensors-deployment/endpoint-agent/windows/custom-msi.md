# Building a custom MSI installer for Windows

> **For basic installation instructions**, see the [Windows Agent Installation](installation.md) guide. It gives the standard EXE and MSI installation methods.

You can white label the LimaCharlie installer for Windows with an MSI wrapper. The wrapper shows your name and your details on the installer. It also makes the installation of the Sensor easier for end users. The instructions below use a third-party tool, [exemsi](https://www.exemsi.com/).

## Prerequisites

1. An MSI wrapper application, such as the exemsi application in the instructions below
2. A digital code signing certificate (optional, but highly recommended)

Without a digital code signing certificate, the installer shows a warning that it is from an unknown publisher.

![UAC Signed](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/uac-signed.png)

- vs -
![UAC Warning](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/uac-warning.png)

## Instructions

1. Download the [LimaCharlie sensor EXE](https://downloads.limacharlie.io/sensor/windows/64)
2. Download the [MSI Wrapper application from exemsi.com](https://exemsi.com)
3. Install the exemsi application on your computer
4. Start the exemsi application. Do the steps of the EXE to MSI Converter Wizard that follow.

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_1_-_First_screen_after_launch.png)

5. Select the executable

    - Set the `Setup executable input file name` to the LimaCharlie EXE that you downloaded
    - Optionally, set an MSI output file name of your choice (for example, Acme\_Installer.msi)
    - Set the MSI platform architecture to match the executable (x86 for 32-bit, and x64 for 64-bit)

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_2_-__Select_the_executable.png)

6. Set the visibility in Apps & features

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_3_-_Visibility_in_Apps_&_features.png)

7. Set the Security and User Context

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_4_-_Security_and_User_Context.png)

8. Specify Application IDs

    - In the Upgrade Code section, click the "Create New" button to generate a code. The code allows uninstallation.

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_5_-_Application_Ids.png)

9. Specify Properties (optional: change these options to show your brand on the installer)

    - Change the drop-down menu of each line item from "Executable" to "Manual" to set your own values for the Product Name, Manufacturer, Version, Comments, and Product icon

### Original

![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_6a_-_Properties_-_Defaults.png)

### Customized

![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_6b_-_Properties_-_Customized.png)

1. Specify More Properties (optional)

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_7_-_More_properties.png)

1. Specify Parameters

    - In the "Install arguments" box, enter "-i", then a space, then your [installation key](../../installation-keys.md)
    - -i YOUR\_INSTALLATION\_KEY\_GOES\_HERE

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_8b_-_Parameters_-_filled.png)

To allow uninstallation, set the Uninstall argument to "-c". You do not need your Installation Key to uninstall.

1. Actions

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_9_-_Actions.png)

1. Summary

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_10_-_Summary.png)

1. Status

    ![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Wrapper_-_11_-_Status.png)

After you create the MSI package, sign it with your digital signature. For more information, see [how to sign the MSI on the exemsi website](https://www.exemsi.com/documentation/sign-your-msi/).

## Experience when running the MSI

When you install the application with the MSI, the title bar shows your application name.

![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/MSI_Installation.png)

When you inspect the properties of the MSI, you see the details that you specified.

![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/Created_MSI_Properties-Details.png)

In the Apps & Features section of Windows, the application shows under your name.

![exemsi](https://storage.googleapis.com/limacharlie-io/doc/white-label/exemsi-instructions/Shown_in_Control_Panel_-_Apps_and_Features.png)
