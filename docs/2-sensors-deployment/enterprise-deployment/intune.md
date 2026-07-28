# Agent Deployment via Microsoft Intune

[Microsoft Intune](https://learn.microsoft.com/en-us/mem/) is a cloud endpoint management solution that integrates with Microsoft Azure. It manages apps and devices on many device types, which include mobile devices, desktop computers, and virtual endpoints.

You can use Intune to deploy the LimaCharlie Sensor in enterprise environments. To add a custom App to Intune, select the `+ Add` button in the Intune admin center:

![image.png](../../assets/images/image(61).png)

InTune supports Windows and macOS package deployment.

## Windows Deployment via Intune

To deploy Windows applications with Intune, you must create an Intune application package (`.intunewin` file extension). Use Microsoft's IntuneWinAppUtil.exe file. See Microsoft's [`.intunewin` packaging documentation](https://learn.microsoft.com/en-us/mem/intune/apps/apps-win32-prepare).

### Intune Package Contents

It is possible that you must create an Intune package for each Organization, because you must give the Installation Key at the time of installation.

LimaCharlie recommends that you first create a [custom MSI installer](../endpoint-agent/windows/custom-msi.md) with the correct installation key. Then include that installer in your `.intunewin` file.

After you click `+ Add`, select `Windows app (Win32)`:

![image.png](../../assets/images/image(63).png)
