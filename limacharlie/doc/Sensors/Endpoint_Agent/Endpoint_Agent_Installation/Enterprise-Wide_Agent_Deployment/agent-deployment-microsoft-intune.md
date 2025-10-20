# Agent Deployment via Microsoft Intune

[Microsoft Intune](https://learn.microsoft.com/en-us/mem/) is a cloud-based endpoint management solution that integrates with Microsoft Azure. It allows for simplified app and device management across a wide range of devices, including mobile devices, desktop computers, and virtual endpoints.

Intune can be used to simplify LimaCharlie Sensor deployment within enterprise environments. To add a custom App to Intune, select the `+ Add` button within the Intune admin center:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2861%29.png)

InTune supports Windows and macOS package deployment.

### Windows Deployment via Intune

Deploying Windows applications via Intune requires creating an Intune application package (`.intunewin` file extension). To do this, please utilize Microsoft's IntuneWinAppUtil.exe file. Usage and documentation on creating an `.intunewin` file can be found [here](https://learn.microsoft.com/en-us/mem/intune/apps/apps-win32-prepare).

Intune Package Contents

Intune packages may need to be created for each Organization, as the Installation Key must be provided at the time of installation.

We recommend first creating a [custom MSI installer](building-a-custom-msi-installer-for-windows.md), bundled with the appropriate installation key, and then including that in your `.intunewin` file.

After clicking `+ Add`, choose `Windows app (Win32)`:

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2863%29.png)
