# macOS Agent Installation via Jamf Now

[Jamf Now](https://www.jamf.com/products/jamf-now/) is an MDM solution that manages Apple devices for small and medium businesses. You can deploy LimaCharlie sensors with Jamf Now to distribute applications and to keep an inventory of devices.

## Prerequisites

- a Jamf Now account;
- a provisioning profile that gives the necessary pre-authorizations for deployment on the clients (see [macOS Agent Installation](installation.md));
- a LimaCharlie Mac Sensor installer package (`.pkg`) that is configured for deployment on the clients.

## Set up your account on Jamf Now

1. Create a Jamf Now account at [https://signup.jamfnow.com](https://signup.jamfnow.com/), and log in.
2. Choose the "APNs" tab in the sidebar, and click "Get Started".
3. Click "Download Certificate Signing Request.plist" and save the plist.
4. Click Next in the lower right.
5. In the "Create an Apple Push Certificate" checklist, click "Open the Apple Push Certificates Portal".
6. Log in with your Apple ID.
7. On the "Apple Push Certificates Portal" page that opens, click the green "Create Certificate" button.
8. Accept the Terms of Use, and click Continue.
9. On the "Create a New Push Certificate" page that opens, specify the plist that you downloaded in step 2, and click Upload.
10. On the "Confirmation" page, click Download and save the new PEM certificate file.
11. Go back to the Jamf Now page from step 5, and click Next in the lower right.
12. On the "Upload Push Certificate" page, specify the PEM file that you downloaded in step 10.
13. Under "Save Your Apple ID", record the Apple ID as Jamf asks, and click Save.

## Prepare the LimaCharlie sensor installer package on Jamf

Before you start, you must have a LimaCharlie Sensor installer package (.pkg) that is configured as you need it.

1. Choose the "Apps" tab in the Jamf Now sidebar. It shows "No apps yet, let's fix that."

2. Click "Add an App".

    ![image.png](../../../assets/images/image(117).png)

3. On the "Add an App" page, click "Upload Your App" in the top menu.

    ![image.png](../../../assets/images/image(118).png)

4. Drag your LC Sensor package installer onto the page to upload it to Jamf. You can also click "browse" to find the file.

5. Give the package a suitable name, and click Done.

    ![image.png](../../../assets/images/image(119).png)

## Prepare the LimaCharlie sensor provisioning on Jamf

1. Choose the "Blueprints" tab in the Jamf Now sidebar.

2. Click "Create New Blueprint" at the top.

    ![image.png](../../../assets/images/image(120).png)

3. Enter a Name and a Description as prompted, and click Save Blueprint.

    ![image.png](../../../assets/images/image(121).png)

4. Click the entry for your new Blueprint.

    ![image.png](../../../assets/images/image(122).png)

5. On the inner tab bar that appears, click "Custom Profiles", and then "Add a Custom Profile".

    ![image.png](../../../assets/images/image(123).png)

6. Drag your LimaCharlie mobileconfig file onto the page to upload it to Jamf. You can also click "browse" to find the file.

    ![image.png](../../../assets/images/image(124).png)

7. Click "Add Custom Profile" in the lower right.

    ![image.png](../../../assets/images/image(125).png)

8. On the inner tab bar, click "Apps", and then click "Add App".

    ![image.png](../../../assets/images/image(126).png)

9. In the list, select the "Install Automatically" checkbox for the installer package that you uploaded before.

    ![image.png](../../../assets/images/image(127).png)

10. Click "Save Changes" in the lower right.

## Prepare Jamf Now to enroll devices

1. Choose the "Devices" tab in the Jamf Now sidebar. It shows "No devices yet, let's fix that."
2. Click "Enable Open Enrollment".
3. On the "Open Enrollment" page, select the "Enable Open Enrollment" checkbox, enter an Access Code as prompted, and click Save Settings.
4. Record the enrollment link that the page shows.

## Enroll a Mac for management in Jamf

These steps assume MacOS 13 (Ventura).

1. On a subject Mac, open the enrollment link from step 4 in the section above.

2. Enter the correct Access Code and user name, and click Start Enrollment.

    ![image.png](../../../assets/images/image(128).png)

3. Save the "enroll.mobileconfig" file that starts to download, then double-click it in the Finder to open it.

4. Open the System Settings app and go to the newly-installed profile.

    1. Choose "Privacy & Security".
    2. Scroll to the bottom, and under the "Others" heading, click "Profiles".

    ![image.png](../../../assets/images/image(129).png)

5. Double-click the " Profile".

    ![image.png](../../../assets/images/image(130).png)

6. Click "Install…" in the lower left.

    ![image.png](../../../assets/images/image(131).png)

7. Authenticate with the correct password at the prompt "Profiles is trying to enroll you in a remote management (MDM) service".

    ![image.png](../../../assets/images/image(132).png)

8. Check that System Settings shows "This Mac is supervised and managed by ".

    ![image.png](../../../assets/images/image(133).png)

## Provision a Mac with the LimaCharlie sensor

1. Choose the "Blueprints" tab in the Jamf Now sidebar.

2. Click the entry for the custom Blueprint that you created from Step 6 onward in the "Prepare the LC sensor package on Jamf" section above.

    ![image.png](../../../assets/images/image(134).png)

3. On the inner tab bar that appears, click "Devices", and then "Add a Device".

    ![image.png](../../../assets/images/image(135).png)

4. Click a device that you want to provision, and then click "Add Devices" in the lower right corner.

    ![image.png](../../../assets/images/image(136).png)

5. After a few moments, check that the provisioning profile and the LimaCharlie sensor are installed on the subject Mac.

    1. The Mac appears in the Jamf Devices list on the Blueprints tab with the label "Settings applied". At first it can show "Settings not applied". Refresh the page.

        ![image.png](../../../assets/images/image(137).png)

    2. On the Mac itself, one more profile appears in System Settings > Privacy & Security > Profiles.

        ![image.png](../../../assets/images/image(138).png)

    3. A "Background Items Added" notification is displayed.

        ![image.png](../../../assets/images/image(139).png)

    4. The RPHCP.app appears in the Applications folder of the Mac, and the rphcp daemon runs.
