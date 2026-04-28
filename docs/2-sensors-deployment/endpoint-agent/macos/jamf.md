# macOS Agent Installation via Jamf Now

[Jamf Now](https://www.jamf.com/products/jamf-now/) is an MDM solution that provides an easy way to manage Apple devices for small and medium-sized businesses. LimaCharlie sensors can be deployed via Jamf Now for easy app distribution and inventory capabilities.

## Prerequisites

- a Jamf Now account;
- a provisioning profile that grants the necessary pre-authorizations (such as is [available here](installation.md)) for deployment on the clients;
- a LimaCharlie Mac Sensor installer package (`.pkg`) that's configured as desired for deployment on the clients.

## Set up your account on Jamf Now

1. Create a Jamf Now account at [https://signup.jamfnow.com](https://signup.jamfnow.com/), and log in.
2. Choose the "APNs" tab in the sidebar, and click "Get Started".
3. Click "Download Certificate Signing Request.plist" and save the plist.
4. Click Next in the lower right.
5. As per the "Create an Apple Push Certificate" checklist shown, click "Open the Apple Push Certificates Portal".
6. Log in with your Apple ID.
7. On the "Apple Push Certificates Portal" page to which you are redirected, click the green "Create Certificate" button.
8. Accept the Terms of Use, and click Continue.
9. On the "Create a New Push Certificate" page to which you're redirected, specify the plist you downloaded in step 2 and click Upload.
10. On the "Confirmation" page, click Download and save the new PEM certificate file.
11. Navigate back to the Jamf Now page as at step 5, and click Next in the lower right.
12. On the "Upload Push Certificate" page, specify the PEM you downloaded in step 10.
13. Under "Save Your Apple ID", annotate same as Jamf invites to do so, and click Save.

## Prepare the LimaCharlie sensor installer package on Jamf

As a prerequisite you must have on hand a LimaCharlie Sensor installer package (.pkg) that's configured as desired.

1. Choose the "Apps" tab in the Jamf Now sidebar. It will show "No apps yet, let's fix that."
2. Click "Add an App".

![image.png](../../../assets/images/image(117).png)

1. On the "Add an App" page, click "Upload Your App" in the top menu.

![image.png](../../../assets/images/image(118).png)

1. Drag your LC Sensor package installer onto the page (or click "browse" to locate it) to upload it to Jamf.
2. Give the package an appropriate name, and click Done.

![image.png](../../../assets/images/image(119).png)

## Prepare the LimaCharlie sensor provisioning on Jamf

1. Choose the "Blueprints" tab in the Jamf Now sidebar.
2. Click "Create New Blueprint" at the top.

![image.png](../../../assets/images/image(120).png)

1. Enter a meaningful Name and Description as prompted, and click Save Blueprint.

![image.png](../../../assets/images/image(121).png)

1. Click on the entry for your new Blueprint.

![image.png](../../../assets/images/image(122).png)

1. On the inner tab bar that appears, click "Custom Profiles", and then "Add a Custom Profile".

![image.png](../../../assets/images/image(123).png)

1. Drag your LimaCharlie mobileconfig file onto the page (or click "browse" to locate it) to upload it to Jamf.

![image.png](../../../assets/images/image(124).png)

1. Click "Add Custom Profile" in the lower right.

![image.png](../../../assets/images/image(125).png)

1. On the inner tab bar, click "Apps", and then click "Add App".

![image.png](../../../assets/images/image(126).png)

1. In the list, enable the "Install Automatically" checkbox for with the installer package that you uploaded earlier.

![image.png](../../../assets/images/image(127).png)

1. Click "Save Changes" in the lower right.

## Prepare Jamf Now to enroll devices

1. Choose the "Devices" tab in the Jamf Now sidebar. It will show "No devices yet, let's fix that."
2. Click "Enable Open Enrollment".
3. On the "Open Enrollment" page, activate the "Enable Open Enrollment" checkbox, enter an Access Code as prompted, and click Save Settings.
4. Take note of the indicated enrollment link.

## Enroll a Mac for management in Jamf

The following recipe presumes the use of MacOS 13 (Ventura).

1. On a subject Mac, visit the enrollment link from step 4 in the section above.
2. Enter the appropriate Access Code and user name, and click Start Enrollment.

![image.png](../../../assets/images/image(128).png)

1. Save the "enroll.mobileconfig" file that begins to download, and then open it in the Finder by double-clicking.
2. Open the System Settings app and navigate to the newly-installed profile.

   1. Choose "Privacy & Security".
   2. Scroll to the bottom, and under the "Others" heading, click "Profiles".

![image.png](../../../assets/images/image(129).png)

1. Double-click on the " Profile".

![image.png](../../../assets/images/image(130).png)

1. Click "Install…" in the lower left.

![image.png](../../../assets/images/image(131).png)

1. Authenticate with the appropriate password when prompted with "Profiles is trying to enroll you in a remote management (MDM) service".

![image.png](../../../assets/images/image(132).png)

1. Observe that System Settings declares "This Mac is supervised and managed by ".

![image.png](../../../assets/images/image(133).png)

## Provision a Mac with the LimaCharlie sensor

1. Choose the "Blueprints" tab in the Jamf Now sidebar.
2. Click the entry for the custom Blueprint you created from Step 6 onward in the "Prepare the LC sensor package on Jamf" section above.

![image.png](../../../assets/images/image(134).png)

1. On the inner tab bar that appears, click "Devices", and then "Add a Device".

![image.png](../../../assets/images/image(135).png)

1. Click on a device you want to provision, and then click "Add Devices" in the lower right corner.

![image.png](../../../assets/images/image(136).png)

1. Observe after a few moments that both the provisioning profile and the LimaCharlie sensor have been installed on the subject Mac.

   1. The Mac appear in the Jamf Devices list on the Blueprints tab with the label "Settings applied". (It may initially appear as "Settings not applied"; simply refresh the page.)

![image.png](../../../assets/images/image(137).png)

1. On the Mac itself, an additional profile appears in System Settings > Privacy & Security > Profiles.

![image.png](../../../assets/images/image(138).png)

1. A "Background Items Added" notification is displayed.

![image.png](../../../assets/images/image(139).png)

1. The RPHCP.app appears in the Mac's Applications folder, and the rphcp daemon is running.
